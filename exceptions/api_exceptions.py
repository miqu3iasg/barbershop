"""
Exceptions raised by the terminal client's HTTP layer (utils/client/) when
talking to the backend API. Kept separate from exceptions/domain_exceptions.py
because these represent transport/response failures, not business rules.
"""


class ApiError(Exception):
    """Generic failure while communicating with the backend API."""

    def __init__(self, message, status_code=None, payload=None):
        super().__init__(message)
        self.status_code = status_code
        self.payload = payload or {}


class ApiConnectionError(ApiError):
    """Raised when the backend is unreachable or takes too long to respond."""


class ResourceNotFoundError(ApiError):
    """Raised when the backend responds with 404 Not Found."""


class ValidationApiError(ApiError):
    """Raised when the backend responds with 400 Bad Request."""
