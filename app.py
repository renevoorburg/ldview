import logging
from flask import Flask, request, render_template, Response, abort, redirect, url_for
from rdflib import Graph, URIRef, ConjunctiveGraph, RDF, BNode
from SPARQLWrapper import SPARQLWrapper, JSON
import config
import json
from collections import defaultdict
from urllib.parse import urlparse, urlunparse, quote
import sys
from uri_utils import transform_uri, is_identity_uri, is_yasgui_uri, shorten_uri, page_uri_to_identity_uri, identity_uri_to_page_uri, matches_known_uri_patterns
from rdf_sources.rdf_source_factory import create_rdf_source
from rdf_sources.rdf_source import ResourceNotFound
from content_negotiation import ContentNegotiator
from inverse_relations import prerender_inverse_relations

# Initialize logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# Create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)

# Add the console handler to the logger
logger.addHandler(ch)

app = Flask(__name__)
app.config.from_object('config')
app.jinja_env.auto_reload = True
app.debug = False

# Configure logging
import logging
logging.basicConfig(level=logging.WARNING)

# Set app logger to WARNING
logging.getLogger('app').setLevel(logging.WARNING)

# Initialize RDF source based on configuration
rdf_source = create_rdf_source()

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
    coordinates_list = []  # Store list of coordinate pairs
    current_coordinates = {'latitude': None, 'longitude': None}  # Store coordinates for current subject

    def find_label(node):
        """Helper function to find the first matching label for a node"""
        for label_predicate in config.LABEL_PREDICATES:
            for s, p, o in graph.triples((node, URIRef(label_predicate), None)):
                return str(o)
        return None

    is_blank = subject_uri.startswith('_:') or subject_uri.startswith('n')  # Also check for 'n' prefix

    # Create the correct node based on whether it's a blank node or URI
    if is_blank:
        if subject_uri.startswith('_:'):
            subject_node = BNode(subject_uri[2:])
        else:
            subject_node = BNode(subject_uri)
    else:
        subject_node = URIRef(subject_uri)

    # First collect types
    type_count = 0
    for s, p, o in graph.triples((subject_node, RDF.type, None)):
        type_uri = str(o)
        types.append(shorten_uri(type_uri))  # Now returns dict with prefix and local
        type_count += 1

    # First find the main label if this is the main subject
    if is_main_subject:
        main_label = find_label(subject_node)

    # Initialize blank_node_relations to ensure it's available for blank nodes
    blank_node_relations = {}

    # Collect all predicates linking from the main subject
    if is_main_subject:
        for s, p, o in graph.triples((subject_node, None, None)):
            linked_subject = str(o)
            predicate_str = shorten_uri(str(p))
            blank_node_relations[linked_subject] = predicate_str

    # Voor niet-main subjects, zoek naar inkomende relaties van het main subject
    relation_to_main = None
    relation_uri = None
    if not is_main_subject:
        for s, p, o in graph.triples((None, None, subject_node)):
            if str(s) == id_uri:  # Als de relatie van het main subject komt
                predicate_str = str(p)
                relation_to_main = shorten_uri(predicate_str)
                relation_uri = predicate_str

    for s, p, o in graph.triples((subject_node, None, None)):
        predicate = str(p)
        obj = str(o)
        
        # Check if this is an image predicate
        if predicate in config.IMAGE_PREDICATES:
            images.append({
                'url': obj,
                'predicate': predicate,
                'predicate_short': shorten_uri(predicate)
            })
            continue

        # Check if this is a coordinate predicate
        if predicate in config.COORDINATE_PREDICATES['latitude']:
            try:
                current_coordinates['latitude'] = float(obj)
            except ValueError:
                pass
        elif predicate in config.COORDINATE_PREDICATES['longitude']:
            try:
                current_coordinates['longitude'] = float(obj)
            except ValueError:
                pass

        # If we have a complete coordinate pair, add it to the list
        if current_coordinates['latitude'] is not None and current_coordinates['longitude'] is not None:
            if is_main_subject:
                current_coordinates['label'] = main_label
            coordinates_list.append(current_coordinates.copy())  # Make a copy to avoid reference issues
            current_coordinates = {'latitude': None, 'longitude': None}  # Reset for next pair

        # For blank nodes, check if they contain coordinates
        if obj.startswith('_:') or obj.startswith('n'):
            blank_node = BNode(obj[2:]) if obj.startswith('_:') else BNode(obj)
            blank_coordinates = {'latitude': None, 'longitude': None}
            
            # Search for coordinates in the blank node
            for s, p, o in graph.triples((blank_node, None, None)):
                if str(p) in config.COORDINATE_PREDICATES['latitude']:
                    try:
                        blank_coordinates['latitude'] = float(o)
                    except ValueError:
                        pass
                elif str(p) in config.COORDINATE_PREDICATES['longitude']:
                    try:
                        blank_coordinates['longitude'] = float(o)
                    except ValueError:
                        pass
            
            # If both coordinates are found in the blank node, add them to the list
            if blank_coordinates['latitude'] is not None and blank_coordinates['longitude'] is not None:
                # Find label for this blank node
                label = find_label(blank_node)
                blank_coordinates['label'] = label
                coordinates_list.append(blank_coordinates)

        # For main subject, check for the first label if we haven't found one yet
        if is_main_subject and main_label is None and predicate in config.LABEL_PREDICATES:
            main_label = obj

        # For main subject, collect all values for the first matching description predicate
        if is_main_subject and predicate in config.DESCRIPTION_PREDICATES:
            if main_description_predicate is None:
                main_description_predicate = predicate
                main_descriptions.append(obj)
            elif predicate == main_description_predicate:
                main_descriptions.append(obj)

        # For all predicates, include in the table
        predicates.append({
            'predicate': predicate,
            'predicate_short': shorten_uri(predicate),
            'object': obj,
            'object_short': shorten_uri(obj),
            'is_blank_object': obj.startswith('_:') or obj.startswith('n')
        })

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
        'images': images if is_main_subject else [],  # Only include images for main subject
        'predicate_groups': predicate_groups,
        'is_blank': is_blank,
        'relation_to_main': relation_to_main,
        'relation_uri': relation_uri,
        'coordinates_list': coordinates_list if coordinates_list else None
    }

def create_rdf_response(graph, request):
    """Create an RDF response based on content negotiation"""
    return ContentNegotiator.get_response(
        graph,
        format_param=request.args.get('format'),
        accept_header=request.headers.get('Accept', 'text/html')
    )

def resolve_uri(uri):
    """
    Resolve a URI and return its representation
    """
    if config.USE_SEMANTIC_REDIRECTS is True:
        page_uri = uri
        id_uri = page_uri_to_identity_uri(uri)
    else:
        page_uri = uri
        id_uri = uri
    
    try:
        rdf_graph = rdf_source.get_rdf_for_uri(id_uri, page_uri)
    except ResourceNotFound as e:
        return render_template('error.html', 
            message=f"404 - Resource not found: {str(e)}",
            uri=uri,
            config=config), 404
    except Exception as e:
        return render_template('error.html',
            message=f"500 - Internal server error: {str(e)}",
            uri=uri,
            config=config), 500

    # Handle content negotiation
    response = ContentNegotiator.get_response(
        rdf_graph,
        format_param=request.args.get('format'),
        accept_header=request.headers.get('Accept', 'text/html')
    )
    if response:
        return response

    # Build the HTML view
    inverse_relations = {}
    if rdf_graph and id_uri is not config.BASE_URI:
        inverse_graph = rdf_source.get_inverse_relations_graph(id_uri)
        inverse_relations = prerender_inverse_relations(inverse_graph, id_uri)
   
    subjects = defaultdict(list)
    blank_nodes = []
    main_subject = None

    # Process each subject in the graph
    for subject in set(rdf_graph.subjects()):
        subject_uri = str(subject)
        if isinstance(subject, BNode):
            # Zoek de relatie tussen main subject en blank node
            relation_to_main = None
            relation_uri = None
            for s, p, o in rdf_graph.triples((URIRef(id_uri), None, subject)):
                relation_to_main = shorten_uri(str(p))
                relation_uri = str(p)
                break
            
            subject_data = process_subject(subject_uri, rdf_graph)
            if subject_data:
                subject_data['relation_to_main'] = relation_to_main
                subject_data['relation_uri'] = relation_uri
                blank_nodes.append(subject_data)
            continue

        subject_data = process_subject(subject_uri, rdf_graph, is_main_subject=(subject_uri == id_uri), id_uri=id_uri)
        if not subject_data:
            continue

        if subject_uri == id_uri:
            main_subject = subject_data
        else:
            subjects[subject_uri].append(subject_data)

    # Convert subjects dict to list
    other_subjects = []
    for subject_uri, subject_list in subjects.items():
        other_subjects.extend(subject_list)

    # Sort subjects
    sorted_subjects = []
    if main_subject:
        sorted_subjects.append(main_subject)
    sorted_subjects.extend(sorted(other_subjects, key=lambda x: x['subject']))
    sorted_subjects.extend(blank_nodes)

    return render_template(
        'view.html',
        subjects=sorted_subjects,
        inverse_relations=inverse_relations,
        config=config,
        shorten_uri=shorten_uri,
        uri=uri,
        query_uri=id_uri,
        query_uri_short=shorten_uri(id_uri),
        blank_nodes=blank_nodes
    )

# Register error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('error.html',
        message="404 - Page not found",
        uri=request.path,
        config=config), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html',
        message="500 - Internal server error",
        uri=request.path,
        config=config), 500

@app.route('/<path:request>')
def handle_uri(request):
    uri = f"{config.BASE_URI}{request}"

    if config.USE_SEMANTIC_REDIRECTS is True and is_identity_uri(uri):
        return redirect(identity_uri_to_page_uri(uri), 303) # see other

    if is_yasgui_uri(uri):
        if config.RDF_DATA_SOURCE_TYPE == 'sparql':
            return render_template('yasgui.html', config=config)
        else:
            return render_template('error.html',
                message="YASGUI interface is only available in SPARQL mode",
                uri=f'/{uri}',
                config=config), 404
    else:
        return resolve_uri(uri)

@app.route('/')
def root():
    """Root URL redirects to base URI"""
    return resolve_uri(config.BASE_URI)

if __name__ == '__main__':
    app.run(debug=False, port=5001)
