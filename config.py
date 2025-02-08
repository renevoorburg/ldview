# Viewing model:
SEMANTIC_REDIRECTS = False

# Semantic redirects setup:
REDIRECT_STATUS_CODE = 303  # See Other
URI_PATTERNS = {
    'id': '/id/',     # Pattern voor identificatie URIs
    'doc': '/doc/'    # Pattern voor document URIs
}

# Source configuration
RDF_SOURCE_TYPE = 'turtlefiles'  # Options: 'sparql', 'turtlefiles'

# Turtle files source configuration
TURTLE_FILES_DIRECTORY = 'resources'  # Directory containing .ttl files
TURTLE_FILES_BASE_URI = 'https://data.digitopia.nl/'  # Base URI for Turtle files


# SPARQL endpoint source configuration
SPARQL_ENDPOINT = "https://data.digitopia.nl/sparql"  # Pas dit aan naar het gewenste endpoint
# SPARQL_ENDPOINT = "https://data.bibliotheken.nl/sparql"  # Pas dit aan naar het gewenste endpoint


KNOWN_URI_PATTERNS = [ 
    'https://data.digitopia.nl/',
]


# Namespace configuration
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

# Content negotiation settings
SUPPORTED_FORMATS = {
    'text/html': 'html',
    'application/rdf+xml': 'xml',
    'text/turtle': 'turtle',
    'application/ld+json': 'json-ld'
}


# Predicaat configuratie voor weergave
LABEL_PREDICATES = [
    'http://www.w3.org/2004/02/skos/core#prefLabel',
    'http://www.w3.org/2000/01/rdf-schema#label',
    'http://purl.org/dc/terms/title',
    'http://purl.org/dc/elements/1.1/title',
    'http://schema.org/name',
    'http://data.bibliotheken.nl/rdanl#preferredNameOfPerson'
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

# Predicaat groepen voor geordende weergave
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
        'http://www.w3.org/2004/02/skos/core#exactMatch'
    ]   
]
