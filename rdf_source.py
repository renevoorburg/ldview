from abc import ABC, abstractmethod
from rdflib import Graph
import logging
from SPARQLWrapper import SPARQLWrapper, JSON
import config

logger = logging.getLogger(__name__)

class ResourceNotFound(Exception):
    """Exception raised when an RDF resource cannot be found"""
    pass

class RDFSource(ABC):
    """
    Abstract base class for RDF data sources
    """
    
    @abstractmethod
    def get_rdf_for_uri(self, id_uri: str, page_uri: str = None) -> Graph:
        """
        Retrieve RDF data for a given URI
        
        Args:
            id_uri: The identity URI to query for
            page_uri: Optional page URI if different from id_uri
            
        Returns:
            Graph: RDFLib Graph containing the RDF data
            
        Raises:
            ResourceNotFound: When the requested resource cannot be found
        """
        pass

    def get_sparql_datasets(self):
        """Get all datasets using SPARQL CONSTRUCT query"""
        try:
            sparql = SPARQLWrapper(config.SPARQL_ENDPOINT)
            sparql.setQuery(config.HOME_PAGE_SPARQL_QUERY)
            sparql.setReturnFormat('xml')
            
            # Create a new graph for the results
            graph = Graph()
            
            # Execute query and parse results into graph
            result = sparql.query().convert()
            if isinstance(result, bytes):
                graph.parse(data=result, format='xml')
            else:
                graph.parse(data=str(result), format='xml')
                
            return graph
        except Exception as e:
            logger.error(f"Error executing SPARQL query for datasets: {str(e)}")
            return None

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
            logger.error(f"Error executing SPARQL query: {str(e)}")
            return []
