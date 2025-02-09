from SPARQLWrapper import SPARQLWrapper
from rdflib import Graph
import logging
import config
from rdf_source import RDFSource, ResourceNotFound

logger = logging.getLogger(__name__)

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
        sparql.setQuery(f"""
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            
            CONSTRUCT {{
                ?s ?p ?o .
                ?o ?p2 ?o2 .
                ?o2 ?p3 ?o3 .
            }}
            WHERE {{
                {{  # First part with id_uri
                    VALUES ?s {{ <{id_uri}> }}
                    {{
                        ?s ?p ?o .
                    }}
                    UNION
                    {{
                        ?s ?p ?o .
                        FILTER(isBlank(?o))
                        ?o ?p2 ?o2 .
                    }}
                    UNION
                    {{
                        ?s ?p ?o .
                        FILTER(isBlank(?o))
                        ?o ?p2 ?o2 .
                        FILTER(isBlank(?o2))
                        ?o2 ?p3 ?o3 .
                    }}
                }}
                UNION
                {{  # Second part with page uri
                    VALUES ?s {{ <{page_uri}> }}
                    {{
                        ?s ?p ?o .
                    }}
                    UNION
                    {{
                        ?s ?p ?o .
                        FILTER(isBlank(?o))
                        ?o ?p2 ?o2 .
                    }}
                    UNION
                    {{
                        ?s ?p ?o .
                        FILTER(isBlank(?o))
                        ?o ?p2 ?o2 .
                        FILTER(isBlank(?o2))
                        ?o2 ?p3 ?o3 .
                    }}
                }}
            }}
        """)
        sparql.setReturnFormat('turtle')
        
        try:
            results = sparql.query().convert()
            
            # Parse into graph
            rdf_graph = Graph()
            if isinstance(results, bytes):
                logger.debug(f"Got bytes result, length: {len(results)}")
                logger.debug(f"Result content: {results[:1000]}")  # First 1000 bytes
                rdf_graph.parse(data=results, format='turtle')
            else:
                logger.debug(f"Got direct graph result, type: {type(results)}")
                rdf_graph = results
                
            if len(rdf_graph) == 0:
                raise ResourceNotFound(f"No data found in SPARQL endpoint for URI: {id_uri}")
                
            return rdf_graph
            
        except Exception as e:
            if isinstance(e, ResourceNotFound):
                raise
            logger.error(f"Error querying SPARQL endpoint for URI {id_uri}: {str(e)}")
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
                logger.error("SPARQL query returned empty graph")
                return None
                
            return rdf_graph
            
        except Exception as e:
            logger.error(f"Error executing SPARQL query for datasets: {str(e)}")
            return None
