"""Custom error classes."""

from http.client import HTTPException


class AuthenticationRequiredError(HTTPException):
    """Raised when there is a problem with authorization during regular requests."""


class AvatarNotFoundError(ValueError):
    """Raised when an invalid avatar is selected to switch to."""
