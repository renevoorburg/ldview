from rdflib import Graph
import os
import logging
import config
from urllib.parse import urlparse
from .rdf_source import RDFSource, ResourceNotFound

logger = logging.getLogger(__name__)

class TurtleFiles(RDFSource):
    """
    RDF source that reads Turtle files from a directory
    """
    
    def __init__(self, base_directory: str, base_uri: str):
        """
        Initialize TurtleFiles source
        
        Args:
            base_directory: Directory containing the Turtle files
            base_uri: Base URI that will be stripped to find the file path
                     (e.g., 'https://data.digitopia.nl/id/')
        """
        self.base_directory = base_directory
        self.base_uri = base_uri
        
    def _uri_to_file_path(self, uri: str) -> str:
        """
        Convert a URI to a file path
        
        Example:
            URI: https://data.digitopia.nl/id/dataset/sporthelden
            Returns: /base/directory/dataset/sporthelden.ttl
        """
        if not uri.startswith(self.base_uri):
            raise ValueError(f"URI {uri} does not start with base URI {self.base_uri}")
            
        relative_path = uri[len(self.base_uri):]
        file_path = os.path.join(self.base_directory, relative_path + '.ttl')
        return file_path
        
    def get_rdf_for_uri(self, id_uri: str, page_uri: str = None) -> Graph:
        if id_uri == config.BASE_URI:
            file_path = os.path.join(self.base_directory, config.HOME_PAGE_TURTLEFILE)
        else:
            file_path = self._uri_to_file_path(id_uri)

        if not os.path.exists(file_path):
            raise ResourceNotFound(f"No Turtle file found for URI: {id_uri}")
                 
        graph = Graph()
        graph.parse(file_path, format='turtle')
        return graph
