"""
exception raise by this package
"""
from typing import Any, Optional

from requests.models import Response


class TransmissionError(Exception):
    """
    This exception is raised when there has occurred an error related to
    communication with Transmission.
    """

    message: str
    method: Optional[Any]  # rpc call method
    argument: Optional[Any]  # rpc call arguments
    response: Optional[Any]  # parsed json response, may be dict with keys 'result' and 'arguments'
    rawResponse: Optional[str]  # raw text http response
    original: Optional[Response]  # original http requests

    def __init__(
        self,
        message: str = "",
        method: Optional[Any] = None,
        argument: Optional[Any] = None,
        response: Optional[Any] = None,
        rawResponse: Optional[str] = None,
        original: Optional[Response] = None,
    ):
        super().__init__()
        self.message = message
        self.method = method
        self.argument = argument
        self.response = response
        self.rawResponse = rawResponse
        self.original = original

    def __str__(self) -> str:
        if self.original:
            original_name = type(self.original).__name__
            return f'{self.message} Original exception: {original_name}, "{self.original}"'
        return self.message


class TransmissionAuthError(TransmissionError):
    """Raised when username or password is incorrect"""


class TransmissionConnectError(TransmissionError):
    """raised when client can't connect to transmission daemon"""


class TransmissionTimeoutError(TransmissionConnectError):
    """Timeout"""
