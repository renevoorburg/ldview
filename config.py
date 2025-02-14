## ldview config ##

BASE_URI = 'https://data.digitopia.nl/'

# Viewing model
USE_SEMANTIC_REDIRECTS = True

# Redirect pattern for segmantic redirecs, when selected:
SEMANTIC_REDIRECT_URI_SEGMENTS = {
    'identification': '/id/',     # Pattern voor identificatie URIs
    'documentation': '/doc/'    # Pattern voor document URIs
}

# Date source configuration
RDF_DATA_SOURCE_TYPE = 'sparql'  # Options: 'sparql', 'turtlefiles'

# turtlefiles -> source configuration:
TURTLE_FILES_DIRECTORY = 'resources'  # Directory containing .ttl files

# sparql -> endpoint configuration:
SPARQL_ENDPOINT = "https://data.digitopia.nl/sparql"  # Pas dit aan naar het gewenste endpoint
# SPARQL_ENDPOINT = "https://data.bibliotheken.nl/sparql"  # Pas dit aan naar het gewenste endpoint

# Content negotiation settings
SUPPORTED_OUTPUT_FORMATS = {
    'text/html': 'html',
    'application/rdf+xml': 'xml',
    'text/turtle': 'turtle',
    'application/ld+json': 'json-ld'
}

# Namespaces as used in 'html' view: 
NAMESPACES = {
    'rdanl': 'http://data.bibliotheken.nl/rdanl#',
    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
    'owl': 'http://www.w3.org/2002/07/owl#',
    'xsd': 'http://www.w3.org/2001/XMLSchema#',
    'skos': 'http://www.w3.org/2004/02/skos/core#',
    'schema': 'http://schema.org/',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'dcterms': 'http://purl.org/dc/terms/'
}

# Predicate config for html viewer:
LABEL_PREDICATES = [
    'http://www.w3.org/2004/02/skos/core#prefLabel',
    'http://www.w3.org/2000/01/rdf-schema#label',
    'http://purl.org/dc/terms/title',
    'http://purl.org/dc/elements/1.1/title',
    'http://schema.org/name',
    'http://data.bibliotheken.nl/rdanl#preferredNameOfPerson',
    'http://data.bibliotheken.nl/rdanl#titleProper',
    'http://data.bibliotheken.nl/rdanl#titleOfWork',
    'http://data.bibliotheken.nl/rdanl#titleOfExpression',
]

DESCRIPTION_PREDICATES = [
    'http://www.w3.org/2004/02/skos/core#definition',
    'http://purl.org/dc/terms/description',
    'http://purl.org/dc/elements/1.1/description',
    'http://schema.org/description',
    'http://www.w3.org/2000/01/rdf-schema#comment',
    'http://data.bibliotheken.nl/rdanl#biographicalInformation'
]

# Image predicates
IMAGE_PREDICATES = {
    'http://xmlns.com/foaf/0.1/depiction',
    'http://schema.org/thumbnailUrl',
    'http://schema.org/image'
}

# Coordinate predicates
COORDINATE_PREDICATES = {
    'latitude': [
        'http://www.w3.org/2003/01/geo/wgs84_pos#lat',
        'http://schema.org/latitude'
    ],
    'longitude': [
        'http://www.w3.org/2003/01/geo/wgs84_pos#long',
        'http://schema.org/longitude'
    ]
}

# Predicate groups for ordered and clustered display:
PREDICATE_GROUPS = [
    [
        'http://www.w3.org/1999/02/22-rdf-syntax-ns#type',
    ],
    [
        'http://www.w3.org/2004/02/skos/core#prefLabel',
        'http://www.w3.org/2000/01/rdf-schema#label',
        'http://purl.org/dc/terms/title',
        'http://purl.org/dc/elements/1.1/title',
        'http://schema.org/name',
        'http://data.bibliotheken.nl/rdanl#preferredNameOfPerson',
        'http://schema.org/familyName',
        'http://schema.org/givenName',
        'http://schema.org/alternateName',
        'http://data.bibliotheken.nl/rdanl#givenName',
        'http://data.bibliotheken.nl/rdanl#surname',
        'http://data.bibliotheken.nl/rdanl#nameOfPerson',
        'http://xmlns.com/foaf/0.1/nick',
        'http://data.bibliotheken.nl/rdanl#accessPointForPerson',
        'http://data.bibliotheken.nl/rdanl#variantAccessPointForPerson'
    ],
    [
        'http://www.w3.org/2004/02/skos/core#definition',
        'http://purl.org/dc/terms/description',
        'http://purl.org/dc/elements/1.1/description',
        'http://schema.org/description',
        'http://www.w3.org/2000/01/rdf-schema#comment',
        'http://data.bibliotheken.nl/rdanl#biographicalInformation'
    ],
    [
        'http://schema.org/nationality',
    ],
    [
        'http://data.bibliotheken.nl/rdanl#dateOfBirth',
        'http://schema.org/birthDate',
        'http://schema.org/birthPlace',
        'http://data.bibliotheken.nl/rdanl#dateOfDeath',
        'http://schema.org/deathDate',
        'http://schema.org/deathPlace'
    ],
    [
        'http://www.w3.org/2004/02/skos/core#broader',
        'http://www.w3.org/2004/02/skos/core#narrower',
        'http://www.w3.org/2004/02/skos/core#related'
    ],
    [
        'http://www.w3.org/2002/07/owl#sameAs',
        'http://www.w3.org/2004/02/skos/core#exactMatch',
        'http://schema.org/sameAs',
        'http://schema.org/mainEntityOfPage',
        'http://www.w3.org/2000/01/rdf-schema#seeAlso'
    ]   
]

# Map configuration
DEFAULT_MAP_ZOOM_LEVEL = 9  # Default zoom level for single point on map

# Homepage configuration
HOME_PAGE_TURTLEFILE = 'index.ttl'  # Turtle file to use for homepage in turtlefiles mode

# Homepage SPARQL query (for sparql mode)
HOME_PAGE_SPARQL_QUERY = """
PREFIX schema: <http://schema.org/>

CONSTRUCT {
  ?s schema:name ?name .
  ?s schema:description ?description .  
} WHERE {
?s a schema:Dataset .
?s schema:name ?name .  
OPTIONAL {
?s schema:description ?description .  
  }  
}
"""

# YASGUI configuration (only used when RDF_DATA_SOURCE_TYPE is 'sparql')
YASGUI_PAGE = 'yasgui'  # Will be accessible at {BASE_URI}{YASGUI_PAGE}

# Display configuration
MAX_INVERSE_SUBJECTS = 5 # Maximum number of subjects to show for inverse relations
