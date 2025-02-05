from flask import Flask, request, render_template, Response, abort, redirect
from rdflib import Graph, URIRef, ConjunctiveGraph, RDF, BNode
from SPARQLWrapper import SPARQLWrapper, JSON
import config
import logging
import json
from urllib.parse import urlparse, urlunparse
from collections import defaultdict
import sys
from uri_utils import transform_uri, is_identity_uri, get_sparql_uri, shorten_uri, page_uri_to_identity_uri, matches_known_uri_patterns
from sparql_utils import SPARQLEndpoint
from turtle_files import TurtleFiles
from rdf_source import ResourceNotFound
from content_negotiation import ContentNegotiator

app = Flask(__name__)

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Initialize RDF source based on configuration
if config.RDF_SOURCE_TYPE == 'sparql':
    rdf_source = SPARQLEndpoint(config.SPARQL_ENDPOINT)
elif config.RDF_SOURCE_TYPE == 'turtlefiles':
    rdf_source = TurtleFiles(config.TURTLE_FILES_DIRECTORY, config.TURTLE_FILES_BASE_URI)
else:
    raise ValueError(f"Unknown RDF source type: {config.RDF_SOURCE_TYPE}")

def find_matching_values(predicates, triples):
    """Find all matching values for a list of predicates, maintaining predicate order"""
    values = []
    for pred in predicates:
        for triple in triples:
            if triple['predicate'] == pred:
                values.append(triple['object'])
    return values

def get_types(triples):
    """Get all rdf:type values"""
    types = []
    for triple in triples:
        if triple['predicate'] == 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type':
            types.append(triple['object_short'])
    return types

def group_predicates(predicates):
    """Group predicates according to configuration"""
    # Initialize result
    result = []
    used_predicates = []  # List to track all used predicates
    
    # Process configured groups
    for group in config.PREDICATE_GROUPS:
        group_predicates = []
        for pred_uri in group:
            # Find all predicates matching this URI
            matching_predicates = [p for p in predicates if p['predicate'] == pred_uri]
            if matching_predicates:
                group_predicates.extend(matching_predicates)
                used_predicates.extend(matching_predicates)
        
        # Only add group if it has predicates
        if group_predicates:
            result.append({'predicates': group_predicates})
    
    # Add remaining predicates
    other_predicates = [p for p in predicates if p not in used_predicates]
    if other_predicates:
        result.append({'predicates': sorted(other_predicates, key=lambda x: x['predicate'])})
    
    return result



def process_subject(subject_uri, graph, is_main_subject=False, id_uri=None):
    """Process a subject URI and return its data"""
    # Get all predicates and objects for this subject
    predicates = []
    types = []
    images = []  # List for image URLs
    main_label = None  # Single label for the header
    main_description_predicate = None  # Track the first matching description predicate
    main_descriptions = []  # Collect all values for the first matching description predicate
    
    is_blank = subject_uri.startswith('_:') or subject_uri.startswith('n')  # Also check for 'n' prefix
    logger.debug(f"Processing subject: {subject_uri} (blank node: {is_blank})")

    # Create the correct node based on whether it's a blank node or URI
    if is_blank:
        if subject_uri.startswith('_:'):
            subject_node = BNode(subject_uri[2:])
        else:
            subject_node = BNode(subject_uri)
        logger.debug(f"Using BNode for blank node: {subject_node}")
    else:
        subject_node = URIRef(subject_uri)
        logger.debug(f"Using URIRef for URI: {subject_node}")
    
    # First collect types
    type_count = 0
    for s, p, o in graph.triples((subject_node, RDF.type, None)):
        type_uri = str(o)
        types.append(shorten_uri(type_uri))  # Now returns dict with prefix and local
        type_count += 1
        logger.debug(f"Found type for {subject_uri}: {type_uri}")
    
    logger.debug(f"Found {type_count} types for subject {subject_uri}")

    # Initialize blank_node_relations to ensure it's available for blank nodes
    blank_node_relations = {}

    # Collect all predicates linking from the main subject
    if is_main_subject:
        for s, p, o in graph.triples((subject_node, None, None)):
            linked_subject = str(o)
            predicate_str = shorten_uri(str(p))
            blank_node_relations[linked_subject] = predicate_str
            logger.debug(f"Link from main subject: {subject_uri} -> {predicate_str} -> {linked_subject}")

    # Voor niet-main subjects, zoek naar inkomende relaties van het main subject
    relation_to_main = None
    if not is_main_subject:
        for s, p, o in graph.triples((None, None, subject_node)):
            if str(s) == id_uri:  # Als de relatie van het main subject komt
                predicate_str = shorten_uri(str(p))
                relation_to_main = predicate_str
                logger.debug(f"Found relation to main: {str(s)} -> {predicate_str} -> {subject_uri}")

    for s, p, o in graph.triples((subject_node, None, None)):
        predicate = str(p)
        obj = str(o)
        logger.debug(f"Found triple: {subject_uri} {predicate} {obj}")

        # Verify predicate
        logger.debug(f"Predicate: {predicate}")

        # Set relation to main subject for linked subjects
        if not is_main_subject:
            logger.debug(f"Relation to main for {subject_uri}: {relation_to_main}")
        
        # Check if this is an image predicate
        if predicate in config.IMAGE_PREDICATES:
            images.append({
                'url': obj,
                'predicate': predicate,
                'predicate_short': shorten_uri(predicate)
            })
            continue

        # For main subject, check for the first label if we haven't found one yet
        if is_main_subject and main_label is None and predicate in config.LABEL_PREDICATES:
            main_label = obj
            logger.debug(f"Set main label for {subject_uri}: {obj}")

        # For main subject, collect all values for the first matching description predicate
        if is_main_subject and predicate in config.DESCRIPTION_PREDICATES:
            if main_description_predicate is None:
                main_description_predicate = predicate
                main_descriptions.append(obj)
                logger.debug(f"Added first description for {subject_uri}: {obj}")
            elif predicate == main_description_predicate:
                main_descriptions.append(obj)
                logger.debug(f"Added additional description for {subject_uri}: {obj}")

        # For all predicates, include in the table
        predicates.append({
            'predicate': predicate,
            'predicate_short': shorten_uri(predicate),
            'object': obj,
            'object_short': shorten_uri(obj),
            'is_blank_object': obj.startswith('_:') or obj.startswith('n')
        })
        pred_count = 0
        pred_count += 1
        logger.debug(f"Added predicate for {subject_uri}: {predicate} -> {obj}")

    logger.debug(f"Found {pred_count} predicates for subject {subject_uri}")

    # Group predicates according to configuration
    predicate_groups = group_predicates(predicates)

    # Combine all descriptions for the first matching predicate into a single string
    main_description = ' '.join(main_descriptions) if main_descriptions else None

    return {
        'subject': subject_uri,
        'subject_short': shorten_uri(subject_uri),
        'types': types,
        'main_label': main_label if is_main_subject else None,
        'main_description': main_description if is_main_subject else None,
        'predicate_groups': predicate_groups,
        'is_blank': is_blank,
        'images': images if is_main_subject else [],  # Only include images for main subject
        'relation_to_main': relation_to_main  # Add relation to main subject for linked subjects
    }

@app.route('/<path:uri>')
def resolve_uri(uri):
    """
    Resolve a URI and return its representation
    """
    if not matches_known_uri_patterns(uri):
        return render_template('error.html', 
            message="404 - URI not found",
            uri=uri), 404

    if is_identity_uri(uri):
        return redirect(page_uri_to_identity_uri(uri))

    page_uri = uri
    id_uri = page_uri_to_identity_uri(uri)
    
    try:
        rdf_graph = rdf_source.get_rdf_for_uri(id_uri, page_uri)
    except ResourceNotFound as e:
        return render_template('error.html', 
            message=f"404 - Resource not found: {str(e)}",
            uri=uri), 404
    except Exception as e:
        logger.error(f"Error retrieving RDF data: {str(e)}")
        return render_template('error.html',
            message=f"500 - Internal server error: {str(e)}",
            uri=uri), 500

    # Handle content negotiation
    response = ContentNegotiator.get_response(
        rdf_graph,
        format_param=request.args.get('format'),
        accept_header=request.headers.get('Accept', 'text/html')
    )
    if response:
        return response

    # Default to HTML
    # Get unique subjects from the graph
    unique_subjects = {str(s) for s in rdf_graph.subjects()}
    logger.debug(f"Unique subjects found: {len(unique_subjects)}")
    logger.debug("All subjects in graph:")
    for s in unique_subjects:
        logger.debug(f"  - {s}")
    
    # Process each unique subject
    subjects = []
    for s in unique_subjects:
        logger.debug(f"\nProcessing subject: {s}")
        subject_data = process_subject(s, rdf_graph, is_main_subject=s == id_uri, id_uri=id_uri)
        subjects.append(subject_data)
    
    # Sort subjects: main subject first, then all others
    main_subject = None
    other_subjects = []
    blank_nodes = []
    
    for subject in subjects:
        logger.debug(f"Sorting subject: {subject['subject']}")
        if subject['subject'] == id_uri:
            logger.debug("  -> This is main subject")
            main_subject = subject
        else:
            logger.debug("  -> This is other subject")
            if subject['is_blank']:
                blank_nodes.append(subject)
            elif subject['subject'] == uri:  # Alleen de opgevraagde URI toevoegen
                other_subjects.append(subject)
    
    # Combine in correct order
    sorted_subjects = []
    if main_subject:
        sorted_subjects.append(main_subject)
    sorted_subjects.extend(sorted(other_subjects, key=lambda x: x['subject']))
    sorted_subjects.extend(blank_nodes)  # Add blank nodes at the end
    
    return render_template('view.html',
        uri=uri,
        query_uri=id_uri,
        query_uri_short=shorten_uri(id_uri),
        subjects=sorted_subjects,
        blank_nodes=blank_nodes  # Only pass actual blank nodes
    )

@app.errorhandler(500)
def internal_error(error):
    if request.accept_mimetypes.best_match(['text/html']):
        return render_template('error.html', error=error), 500
    return str(error), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
