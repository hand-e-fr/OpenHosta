from __future__ import annotations

__all__ = (
    "RequestError",
    "ApiKeyError",
    "FrameError",
)

class OhErrorMixin(Exception):
    """ Base class for other customs exceptions """

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return f"{self.message}\n"


class RequestError(OhErrorMixin):
    """ Raised when a request to a llm went wrong """

class RateLimitError(RequestError):
    """ Raised when rate limit is exceeded """

class ApiKeyError(RequestError):
    """ Raised when API key is missing or incorrect """


class FrameError(OhErrorMixin):
    """ Raised when the frame inspection fail """


# création d'agent + multimodal + tools
