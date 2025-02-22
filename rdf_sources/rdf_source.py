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

    @abstractmethod
    def get_inverse_relations_graph(self, id_uri: str) -> Graph:
        """
        Get a graph containing all inverse relations for a given URI.
        
        Args:
            id_uri: The URI to find inverse relations for
            
        Returns:
            Graph: RDFLib Graph containing all triples where id_uri is the object
        """
        pass
