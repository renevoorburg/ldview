from urllib.parse import quote
import config
from rdflib import Graph, URIRef

def prerender_inverse_relations(graph: Graph, id_uri: str) -> dict:
    """
    Process an RDF graph containing inverse relations to prepare it for view presentation.
    The output structure matches exactly that of get_inverse_relations().
    
    Args:
        graph: RDFLib Graph containing the inverse relations
        id_uri: The URI that was used as object in the inverse relations
        
    Returns:
        dict: Dictionary containing inverse relations grouped by predicate, with counts and YASGUI links
    """
    inverse_relations = {}
    
    # First pass: collect all predicates and their subjects
    for s, p, o in graph:
        if str(o) != id_uri:
            continue
            
        pred = str(p)
        subj = str(s)
        
        if pred not in inverse_relations:
            inverse_relations[pred] = []
            
        # Get label if available
        label = ''
        for label_pred in config.LABEL_PREDICATES:
            for label_obj in graph.objects(s, URIRef(label_pred)):
                label = str(label_obj)
                break
            if label:
                break
                
        if len(inverse_relations[pred]) < config.MAX_INVERSE_SUBJECTS:
            inverse_relations[pred].append({
                'uri': subj,
                'label': label
            })
    
    # Second pass: structure the results with counts and YASGUI links where needed
    for pred in list(inverse_relations.keys()):  # Use list() to avoid dictionary size change during iteration
        # Count total subjects for this predicate
        total_count = sum(1 for s, p, o in graph if str(p) == pred and str(o) == id_uri)
        
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
    
    return inverse_relations
