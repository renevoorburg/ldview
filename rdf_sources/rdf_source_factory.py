import config
from .sparql_endpoint import SPARQLEndpoint
from .turtle_files import TurtleFiles
from .rdf_source import RDFSource

def create_rdf_source() -> RDFSource:
    """
    Factory function that creates and returns the appropriate RDF source based on configuration.
    
    Returns:
        RDFSource: Either a SPARQLEndpoint or TurtleFiles instance depending on config.RDF_DATA_SOURCE_TYPE
        
    Raises:
        ValueError: If an invalid RDF_DATA_SOURCE_TYPE is configured
    """
    if config.RDF_DATA_SOURCE_TYPE == 'sparql':
        return SPARQLEndpoint(config.SPARQL_ENDPOINT, config.BASE_URI)
    elif config.RDF_DATA_SOURCE_TYPE == 'turtlefiles':
        return TurtleFiles(config.TURTLE_FILES_DIRECTORY, config.BASE_URI)
    else:
        raise ValueError(f"Invalid RDF_DATA_SOURCE_TYPE in config: {config.RDF_DATA_SOURCE_TYPE}")
