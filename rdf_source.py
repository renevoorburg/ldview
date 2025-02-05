from abc import ABC, abstractmethod
from rdflib import Graph
import logging

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
