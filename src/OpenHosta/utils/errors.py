from __future__ import annotations

__all__ = (
    "RequestError",
    "ApiKeyError",
    "FrameError",
)

class RequestError(Exception):
    """ Raised when a request to a llm went wrong """

class RateLimitError(RequestError):
    """ Raised when rate limit is exceeded """

class ApiKeyError(RequestError):
    """ Raised when API key is missing or incorrect """


class FrameError(Exception):
    """ Raised when the frame inspection fail """

class UncertaintyError(Exception):
    """ Raised when the model is uncertain about its answer """
    pass

class ModelMissingCapabilityError(Exception):
    """ Raised when the model is missing a capability required for uncertainty estimation """

class ModelMissingLogprobsError(Exception):
    """ Raised when the model does not support logprobs """

# création d'agent + multimodal + tools
