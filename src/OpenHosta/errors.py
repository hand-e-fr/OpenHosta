class OhCustomError(Exception):
    """Base class for other customs exceptions"""
    pass
    
class RequestError(OhCustomError):
    """Raised when a request to a llm went wrong"""
    pass
    