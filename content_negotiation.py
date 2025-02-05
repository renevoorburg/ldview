from flask import Response
from rdflib import Graph
import logging

logger = logging.getLogger(__name__)

class ContentNegotiator:
    """
    Handle content negotiation for RDF data
    """
    
    FORMATS = {
        'xml': {
            'format': 'xml',
            'content_type': 'application/rdf+xml; charset=utf-8',
            'mime_type': 'application/rdf+xml'
        },
        'turtle': {
            'format': 'turtle',
            'content_type': 'text/turtle; charset=utf-8',
            'mime_type': 'text/turtle'
        },
        'json-ld': {
            'format': 'json-ld',
            'content_type': 'application/ld+json; charset=utf-8',
            'mime_type': 'application/ld+json'
        }
    }
    
    @classmethod
    def get_response(cls, graph: Graph, format_param: str = None, accept_header: str = None) -> Response:
        """
        Get the appropriate response based on the format parameter or accept header
        
        Args:
            graph: The RDF graph to serialize
            format_param: Optional format parameter from URL
            accept_header: Optional HTTP accept header
            
        Returns:
            Response: Flask response with the appropriate content type and serialized data
        """
        # First try format parameter
        if format_param and format_param in cls.FORMATS:
            format_info = cls.FORMATS[format_param]
            return cls._create_response(graph, format_info)
            
        # Then try accept header
        if accept_header:
            for format_info in cls.FORMATS.values():
                if accept_header == format_info['mime_type']:
                    return cls._create_response(graph, format_info)
                    
        # No matching format found, return None to indicate HTML should be used
        return None
    
    @staticmethod
    def _create_response(graph: Graph, format_info: dict) -> Response:
        """
        Create a Flask response with the serialized graph
        
        Args:
            graph: The RDF graph to serialize
            format_info: Dictionary containing format information
            
        Returns:
            Response: Flask response with the appropriate content type and serialized data
        """
        return Response(
            graph.serialize(format=format_info['format']),
            content_type=format_info['content_type']
        )
