import config

def transform_uri(uri, from_pattern, to_pattern):
    """
    Transform URI by replacing one pattern with another
    """
    if from_pattern in uri:
        return uri.replace(from_pattern, to_pattern)
    return uri


def is_identity_uri(uri):
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

def shorten_uri(uri):
    """
    Shorten a URI by using common prefixes, returns dict with prefix and local
    """
    if not isinstance(uri, str):
        return {'prefix': '', 'local': str(uri)}
    
    if uri.startswith('_:'):
        return {'prefix': '', 'local': uri}
        
    for prefix, namespace in config.NAMESPACES.items():
        if uri.startswith(namespace):
            return {
                'prefix': prefix + ':',
                'local': uri[len(namespace):]
            }
    return {'prefix': '', 'local': uri}

def page_uri_to_identity_uri(uri):
    """
    Convert document URI to id URI if needed
    """
    if config.URI_PATTERNS['doc'] in uri:
        return transform_uri(uri, config.URI_PATTERNS['doc'], config.URI_PATTERNS['id'])
    return uri

def identity_uri_to_page_uri(uri):
    """
    Convert id URI to document URI if needed
    """
    if config.URI_PATTERNS['doc'] in uri:
        return transform_uri(uri, config.URI_PATTERNS['id'], config.URI_PATTERNS['doc'])
    return uri

def matches_known_uri_patterns(uri):
    """
    Check if the URI is accessible
    """
    for pattern in config.KNOWN_URI_PATTERNS:
        if uri.startswith(pattern):
            return True
    return False