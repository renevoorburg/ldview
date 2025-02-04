from flask import Flask, request, render_template, Response, abort, redirect
from rdflib import Graph, URIRef, ConjunctiveGraph, RDF, BNode
from SPARQLWrapper import SPARQLWrapper, JSON
import config
import logging
import json
from urllib.parse import urlparse, urlunparse
from collections import defaultdict
import sys

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

def transform_uri(uri, from_pattern, to_pattern):
    """
    Transform URI by replacing one pattern with another
    """
    if from_pattern in uri:
        return uri.replace(from_pattern, to_pattern)
    return uri

def should_redirect(uri):
    """
    Check if the URI should be redirected (contains /id/)
    """
    return config.URI_PATTERNS['id'] in uri

def get_sparql_uri(uri):
    """
    Get the URI to use for SPARQL query, transforming /doc/ to /id/
    """
    if config.URI_PATTERNS['doc'] in uri:
        return transform_uri(uri, config.URI_PATTERNS['doc'], config.URI_PATTERNS['id'])
    return uri

def query_sparql_endpoint(uri):
    """
    Query the SPARQL endpoint to get equivalent URI and its properties
    """
    # Transform URI for SPARQL query if needed
    query_uri = get_sparql_uri(uri)
    
    sparql = SPARQLWrapper(config.SPARQL_ENDPOINT)
    sparql.setTimeout(10)  # Set 10 second timeout
    sparql.setQuery(f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        
        CONSTRUCT {{
            ?s ?p ?o .
            ?o ?p2 ?o2 .
            ?o2 ?p3 ?o3 .
        }}
        WHERE {{
            {{  # First part with query_uri
                VALUES ?s {{ <{query_uri}> }}
                {{
                    ?s ?p ?o .
                }}
                UNION
                {{
                    ?s ?p ?o .
                    FILTER(isBlank(?o))
                    ?o ?p2 ?o2 .
                }}
                UNION
                {{
                    ?s ?p ?o .
                    FILTER(isBlank(?o))
                    ?o ?p2 ?o2 .
                    FILTER(isBlank(?o2))
                    ?o2 ?p3 ?o3 .
                }}
            }}
            UNION
            {{  # Second part with original request uri
                VALUES ?s {{ <{uri}> }}
                {{
                    ?s ?p ?o .
                }}
                UNION
                {{
                    ?s ?p ?o .
                    FILTER(isBlank(?o))
                    ?o ?p2 ?o2 .
                }}
                UNION
                {{
                    ?s ?p ?o .
                    FILTER(isBlank(?o))
                    ?o ?p2 ?o2 .
                    FILTER(isBlank(?o2))
                    ?o2 ?p3 ?o3 .
                }}
            }}
        }}
    """)
    sparql.setReturnFormat('turtle')
    
    try:
        result = sparql.queryAndConvert()
        logger.info(f"Query result type: {type(result)}")
        logger.info(f"Query result: {result}")
        return result
    except Exception as e:
        logger.error(f"SPARQL query failed: {str(e)}")
        raise

def shorten_uri(uri):
    """
    Vervang namespace URIs met geconfigureerde prefixes
    """
    for prefix, ns_uri in config.NAMESPACES.items():
        if uri.startswith(ns_uri):
            return f"{prefix}:{uri[len(ns_uri):]}"
    return uri

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

def uri_to_id(uri):
    """
    Convert document URI to id URI if needed
    """
    if config.URI_PATTERNS['doc'] in uri:
        return transform_uri(uri, config.URI_PATTERNS['doc'], config.URI_PATTERNS['id'])
    return uri

def process_subject(subject_uri, graph, is_main_subject=False):
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
        types.append(shorten_uri(type_uri))
        type_count += 1
        logger.debug(f"Found type for {subject_uri}: {type_uri}")

    logger.debug(f"Found {type_count} types for subject {subject_uri}")

    # Then process other predicates
    pred_count = 0
    for s, p, o in graph.triples((subject_node, None, None)):
        predicate = str(p)
        obj = str(o)
        logger.debug(f"Found triple: {subject_uri} {predicate} {obj}")

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
        'images': images if is_main_subject else []  # Only include images for main subject
    }

@app.route('/<path:uri>')
def resolve_uri(uri):
    """
    Resolve a URI and return its representation
    """
    try:
        # Convert document URI to id URI if needed
        query_uri = uri_to_id(uri)
        if not query_uri:
            return render_template('error.html', 
                message="Invalid URI pattern",
                uri=uri), 400
        
        # Query the endpoint
        sparql = SPARQLWrapper(config.SPARQL_ENDPOINT)
        sparql.setTimeout(10)  # Set 10 second timeout
        sparql.setQuery(f"""
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            
            CONSTRUCT {{
                ?s ?p ?o .
                ?o ?p2 ?o2 .
                ?o2 ?p3 ?o3 .
            }}
            WHERE {{
                {{  # First part with query_uri
                    VALUES ?s {{ <{query_uri}> }}
                    {{
                        ?s ?p ?o .
                    }}
                    UNION
                    {{
                        ?s ?p ?o .
                        FILTER(isBlank(?o))
                        ?o ?p2 ?o2 .
                    }}
                    UNION
                    {{
                        ?s ?p ?o .
                        FILTER(isBlank(?o))
                        ?o ?p2 ?o2 .
                        FILTER(isBlank(?o2))
                        ?o2 ?p3 ?o3 .
                    }}
                }}
                UNION
                {{  # Second part with original request uri
                    VALUES ?s {{ <{uri}> }}
                    {{
                        ?s ?p ?o .
                    }}
                    UNION
                    {{
                        ?s ?p ?o .
                        FILTER(isBlank(?o))
                        ?o ?p2 ?o2 .
                    }}
                    UNION
                    {{
                        ?s ?p ?o .
                        FILTER(isBlank(?o))
                        ?o ?p2 ?o2 .
                        FILTER(isBlank(?o2))
                        ?o2 ?p3 ?o3 .
                    }}
                }}
            }}
        """)
        sparql.setReturnFormat('turtle')
        
        results = sparql.query().convert()
        logger.debug(f"Query executed successfully")
        
        # Parse into graph
        g = Graph()
        if isinstance(results, bytes):
            logger.debug(f"Got bytes result, length: {len(results)}")
            logger.debug(f"Result content: {results[:1000]}")  # First 1000 bytes
            g.parse(data=results, format='turtle')
        else:
            logger.debug(f"Got direct graph result, type: {type(results)}")
            g = results
            
        # Get the accept header and format parameter
        accept_header = request.headers.get('Accept', 'text/html')
        format_param = request.args.get('format')

        # Determine the format to return
        if format_param:
            if format_param == 'xml':
                return Response(g.serialize(format='xml'),
                            content_type='application/rdf+xml; charset=utf-8')
            elif format_param == 'turtle':
                return Response(g.serialize(format='turtle'),
                            content_type='text/turtle; charset=utf-8')
            elif format_param == 'json-ld':
                return Response(g.serialize(format='json-ld'),
                            content_type='application/ld+json; charset=utf-8')
        elif accept_header:
            if accept_header == 'application/rdf+xml':
                return Response(g.serialize(format='xml'),
                            content_type='application/rdf+xml; charset=utf-8')
            elif accept_header == 'text/turtle':
                return Response(g.serialize(format='turtle'),
                            content_type='text/turtle; charset=utf-8')
            elif accept_header == 'application/ld+json':
                return Response(g.serialize(format='json-ld'),
                            content_type='application/ld+json; charset=utf-8')

        # Default to HTML
        # Get unique subjects from the graph
        unique_subjects = {str(s) for s in g.subjects()}
        logger.debug(f"Unique subjects found: {len(unique_subjects)}")
        for s in unique_subjects:
            logger.debug(f"Subject: {s}")
        
        # Process each unique subject
        subjects = []
        for s in unique_subjects:
            logger.debug(f"\nProcessing subject: {s}")
            subject_data = process_subject(s, g, is_main_subject=s == query_uri)
            logger.debug(f"Subject data:")
            logger.debug(f"  Types: {subject_data['types']}")
            logger.debug(f"  Is blank: {subject_data['is_blank']}")
            logger.debug(f"  Predicate groups: {subject_data['predicate_groups']}")
            logger.debug("---")
            subjects.append(subject_data)
        
        # Sort subjects: main subject first, then blank nodes, then others
        main_subject = None
        blank_nodes = []
        other_subjects = []
        
        for subject in subjects:
            if subject['subject'] == query_uri:
                main_subject = subject
                logger.debug(f"Found main subject: {query_uri}")
            elif subject['subject'].startswith('_:'):
                blank_nodes.append(subject)
                logger.debug(f"Found blank node: {subject['subject']}")
            else:
                other_subjects.append(subject)
                logger.debug(f"Found other subject: {subject['subject']}")
        
        logger.debug(f"Total subjects: {len(subjects)}")
        logger.debug(f"Blank nodes found: {len(blank_nodes)}")
        
        # Combine in correct order
        sorted_subjects = []
        if main_subject:
            sorted_subjects.append(main_subject)
        sorted_subjects.extend(sorted(blank_nodes, key=lambda x: x['subject']))
        sorted_subjects.extend(sorted(other_subjects, key=lambda x: x['subject']))

        logger.debug(f"Final sorted subjects: {len(sorted_subjects)}")
        
        return render_template('view.html',
            uri=uri,
            query_uri=query_uri,
            query_uri_short=shorten_uri(query_uri),
            subjects=sorted_subjects
        )
            
    except Exception as e:
        logging.exception("Error processing request")
        return render_template('error.html',
            message=str(e),
            uri=uri), 500

@app.errorhandler(500)
def internal_error(error):
    if request.accept_mimetypes.best_match(['text/html']):
        return render_template('error.html', error=error), 500
    return str(error), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
