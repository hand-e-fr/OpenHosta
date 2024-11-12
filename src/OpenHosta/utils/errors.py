from __future__ import annotations

from typing import Literal

__all__ = (
    "RequestError",
    "ApiKeyError",
    "FrameError",
    "InvalidStructureError"
)

OhErrorCodes = Literal[
    ""
]


class OhErrorMixin(Exception):
    """ Base class for other customs exceptions """

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return f"{self.message}\n"


class RequestError(OhErrorMixin):
    """ Raised when a request to a llm went wrong """


class ApiKeyError(RequestError):
    """ Raised when API key is missing or incorrect """


class FrameError(OhErrorMixin):
    """ Raised when the frame inspection fail """


class InvalidStructureError(OhErrorMixin):
    """ Raised when the bosy's function aren't placed correctly """


# création d'agent + multimodal + tools
