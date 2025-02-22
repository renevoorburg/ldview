from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib import Graph
import config
from .rdf_source import RDFSource, ResourceNotFound
import logging

logger = logging.getLogger(__name__)

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
                rdf_graph = results
                
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

    def get_inverse_relations_graph(self, id_uri: str) -> Graph:
        """
        Get a graph containing all inverse relations for a given URI using a CONSTRUCT query.
        
        Args:
            id_uri: The URI to find inverse relations for
            
        Returns:
            Graph: RDFLib Graph containing all triples where id_uri is the object,
                  including label predicates from config.LABEL_PREDICATES
        """
        # Build CONSTRUCT query that includes both the inverse relations and their labels
        label_optionals = " ".join(f"OPTIONAL {{ ?s <{pred}> ?label }}" for pred in config.LABEL_PREDICATES)
        construct_query = f"""
            CONSTRUCT {{
                ?s ?p <{id_uri}> .
                ?s ?label_pred ?label .
            }}
            WHERE {{
                ?s ?p <{id_uri}> .
                FILTER(!isBlank(?s))
                {label_optionals}
            }}
        """
        
        # Execute query and return the resulting graph
        sparql = SPARQLWrapper(self.endpoint_url)
        sparql.setQuery(construct_query)
        sparql.setReturnFormat('turtle')  # Get result as Turtle format
        
        try:
            result = sparql.queryAndConvert()
            graph = Graph()
            graph.parse(data=result, format='turtle')
            return graph
        except Exception as e:
            logger.error(f"Error getting inverse relations graph: {str(e)}")
            return Graph()
