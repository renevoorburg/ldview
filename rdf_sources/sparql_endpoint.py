from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib import Graph
import config
from .rdf_source import RDFSource, ResourceNotFound

class SPARQLEndpoint(RDFSource):
    """
    RDF source that queries a SPARQL endpoint
    """
    
    def __init__(self, endpoint_url: str, base_uri: str):
        """
        Initialize SPARQLEndpoint source
        
        Args:
            endpoint_url: URL of the SPARQL endpoint
            base_uri: Base URI for the RDF data (e.g., 'https://data.digitopia.nl/')
        """
        self.endpoint_url = endpoint_url
        self.base_uri = base_uri
        
    def get_rdf_for_uri(self, id_uri: str, page_uri: str = None) -> Graph:
        if page_uri is None:
            page_uri = id_uri

        sparql = SPARQLWrapper(self.endpoint_url)
        sparql.setTimeout(10)  # Set 10 second timeout

        if id_uri == config.BASE_URI:
            sparql.setQuery(config.HOME_PAGE_SPARQL_QUERY)
        else:
            query = config.SPARQL_CONSTRUCT_QUERY.replace("{id_uri}", id_uri).replace("{page_uri}", page_uri)
            sparql.setQuery(query)

        sparql.setReturnFormat('turtle')
        
        try:
            results = sparql.query().convert()
            rdf_graph = Graph()
            if isinstance(results, bytes):
                rdf_graph.parse(data=results, format='turtle')
            else:
                rdf_graph = result
                
            if len(rdf_graph) == 0:
                raise ResourceNotFound(f"No data found in SPARQL endpoint for URI: {id_uri}")
            return rdf_graph
        except Exception as e:
            raise

    def query(self, sparql_query: str):
        """Execute a SPARQL query and return the results"""
        try:
            sparql = SPARQLWrapper(config.SPARQL_ENDPOINT)
            sparql.setQuery(sparql_query)
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
            if isinstance(results, dict) and 'results' in results and 'bindings' in results['results']:
                return results['results']['bindings']
            return []
        except Exception as e:
            raise

