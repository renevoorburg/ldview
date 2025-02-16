from SPARQLWrapper import SPARQLWrapper
from rdflib import Graph
import config
from rdf_source import RDFSource, ResourceNotFound

class SPARQLEndpoint(RDFSource):
    """
    RDF source that queries a SPARQL endpoint
    """
    
    def __init__(self, endpoint_url: str):
        self.endpoint_url = endpoint_url
        
    def get_rdf_for_uri(self, id_uri: str, page_uri: str = None) -> Graph:
        """
        Query the SPARQL endpoint for a given URI and return an RDF graph
        
        Args:
            id_uri: The identity URI to query for
            page_uri: Optional page URI if different from id_uri
            
        Returns:
            Graph: RDFLib Graph containing the RDF data
            
        Raises:
            ResourceNotFound: When no data is found for the given URI
        """
        if page_uri is None:
            page_uri = id_uri

        sparql = SPARQLWrapper(self.endpoint_url)
        sparql.setTimeout(10)  # Set 10 second timeout
        query = config.SPARQL_CONSTRUCT_QUERY.replace("{id_uri}", id_uri).replace("{page_uri}", page_uri)
        sparql.setQuery(query)
        sparql.setReturnFormat('turtle')
        
        try:
            results = sparql.query().convert()
            
            # Parse into graph
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

    def get_sparql_datasets(self):
        """Get all datasets using SPARQL CONSTRUCT query"""
        sparql = SPARQLWrapper(self.endpoint_url)
        sparql.setTimeout(10)  # Set 10 second timeout
        sparql.setQuery(config.HOME_PAGE_SPARQL_QUERY)
        sparql.setReturnFormat('turtle')
        
        try:
            results = sparql.query().convert()
            
            # Parse into graph
            rdf_graph = Graph()
            if isinstance(results, bytes):
                rdf_graph.parse(data=results, format='turtle')
            else:
                rdf_graph.parse(data=str(results), format='turtle')
                
            if len(rdf_graph) == 0:
                return None
                
            return rdf_graph
            
        except Exception as e:
            return None
