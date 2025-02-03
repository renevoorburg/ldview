# SPARQL endpoint configuratie
SPARQL_ENDPOINT = "https://data.digitopia.nl/sparql"  # Pas dit aan naar het gewenste endpoint

# Namespace configuratie
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

# URI pattern configuratie
URI_PATTERNS = {
    'id': '/id/',     # Pattern voor identificatie URIs
    'doc': '/doc/'    # Pattern voor document URIs
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
        'http://schema.org/birthDate',
        'http://schema.org/deathDate',
        'http://data.bibliotheken.nl/rdanl#dateOfBirth',
        'http://data.bibliotheken.nl/rdanl#dateOfDeath'
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

# HTTP status codes
REDIRECT_STATUS_CODE = 303  # See Other
