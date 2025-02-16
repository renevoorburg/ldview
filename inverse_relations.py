from urllib.parse import quote
import config

def get_inverse_relations(rdf_source, id_uri):
    """
    Get inverse relations for a given URI using SPARQL queries.
    
    Args:
        rdf_source: The RDF source to query
        id_uri: The URI to find inverse relations for
        
    Returns:
        dict: Dictionary containing inverse relations grouped by predicate
    """
    inverse_relations = {}
    try:
        # Query for inverse relations
        label_optionals = " ".join(f"OPTIONAL {{ ?s <{pred}> ?label }}" for pred in config.LABEL_PREDICATES)
        inverse_query = f"""
            SELECT DISTINCT ?p ?s ?label WHERE {{
                ?s ?p <{id_uri}> .
                FILTER(!isBlank(?s))
                {label_optionals}
            }} 
            ORDER BY ?p ?s
        """
        inverse_results = rdf_source.query(inverse_query)
        # Group results by predicate
        inverse_relations = {}
        for result in inverse_results:
            pred = result['p']['value']
            subj = result['s']['value']
            label = result.get('label', {}).get('value', '')
            
            if pred not in inverse_relations:
                inverse_relations[pred] = []
            
            if len(inverse_relations[pred]) < config.MAX_INVERSE_SUBJECTS:
                inverse_relations[pred].append({
                    'uri': subj,
                    'label': label  # Gebruik de URI zelf als label
                })
        
        # Build YASGUI links for predicates with more results
        for pred in inverse_relations:
            # Count total results for this predicate
            count_query = f"""
                SELECT (COUNT(DISTINCT ?s) as ?count) WHERE {{
                    ?s <{pred}> <{id_uri}> .
                    FILTER(!isBlank(?s))
                }}
            """
            count_results = rdf_source.query(count_query)
            total_count = int(count_results[0]['count']['value']) if count_results else 0
            
            # Build YASGUI URL if we have more results than shown
            if total_count > config.MAX_INVERSE_SUBJECTS:
                yasgui_url = '/' + config.YASGUI_PAGE.strip('/') + '#'
                
                # Build YASGUI query
                label_optionals = "\n  ".join(f"OPTIONAL {{ ?s <{pred}> ?label }}" for pred in config.LABEL_PREDICATES)
                yasgui_query = f"""
SELECT ?s ?label WHERE {{
  ?s <{pred}> <{id_uri}> .
  FILTER(!isBlank(?s))
  {label_optionals}
}} ORDER BY ?s
                """
                
                yasgui_params = {
                    'query': yasgui_query,
                    'endpoint': config.SPARQL_ENDPOINT,
                    'requestMethod': 'POST',
                    'tabTitle': f'Inverse relations for {id_uri}',
                    'headers': '{}'
                }
                
                param_strings = []
                for key, value in yasgui_params.items():
                    param_strings.append(f"{key}={quote(value)}")
                yasgui_url += '&'.join(param_strings)
                
                # Add URL to the results
                inverse_relations[pred] = {
                    'subjects': inverse_relations[pred],
                    'total_count': total_count,
                    'yasgui_url': yasgui_url
                }
            else:
                # Just wrap the subjects in a dict for consistent structure
                inverse_relations[pred] = {
                    'subjects': inverse_relations[pred],
                    'total_count': total_count
                }
    except Exception as e:
        inverse_relations = {}
    return inverse_relations
