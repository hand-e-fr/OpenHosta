from typing import Literal

OhErrorCodes = Literal[
    ""
]

class OhErrorMixin(Exception):
    """Base class for other customs exceptions"""

    pass
    
class RequestError(OhErrorMixin):
    """Raised when a request to a llm went wrong"""
    pass

class ApiKeyError():
    pass
