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
    return config.SEMANTIC_REDIRECT_URI_SEGMENTS['identification'] in uri


def get_sparql_uri(uri):
    """
    Get the URI to use for SPARQL query, transforming /doc/ to /id/
    """
    if config.SEMANTIC_REDIRECT_URI_SEGMENTS['documentation'] in uri:
        return transform_uri(uri, config.SEMANTIC_REDIRECT_URI_SEGMENTS['documentation'], config.SEMANTIC_REDIRECT_URI_SEGMENTS['identification'])
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
    if config.SEMANTIC_REDIRECT_URI_SEGMENTS['documentation'] in uri:
        return transform_uri(uri, config.SEMANTIC_REDIRECT_URI_SEGMENTS['documentation'], config.SEMANTIC_REDIRECT_URI_SEGMENTS['identification'])
    return uri

def identity_uri_to_page_uri(uri):
    """
    Convert id URI to document URI if needed
    """
    if config.SEMANTIC_REDIRECT_URI_SEGMENTS['identification'] in uri:
        return transform_uri(uri, config.SEMANTIC_REDIRECT_URI_SEGMENTS['identification'], config.SEMANTIC_REDIRECT_URI_SEGMENTS['documentation'])
    return uri

def matches_known_uri_patterns(uri):
    """
    Check if the URI is accessible
    """
    for pattern in config.BASE_URI:
        if uri.startswith(pattern):
            return True
    return False