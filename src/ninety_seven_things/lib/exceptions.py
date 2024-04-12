"""
Into each program some exceptions must raise
"""

# Standard Library Imports
from dataclasses import dataclass


@dataclass
class NinetySevenThingsException(Exception):
    """
    Base exception class
    """

@dataclass
class MessageExceptionMixin:
    message: str


@dataclass
class ConfigurationException(NinetySevenThingsException):
    """
    Configuration Error
    """


@dataclass
class AuthenticationException(NinetySevenThingsException):
    pass


@dataclass
class AuthorisationException(NinetySevenThingsException):
    pass


@dataclass
class SearchException(NinetySevenThingsException, MessageExceptionMixin):
    pass


@dataclass
class DoesNotExistException(NinetySevenThingsException, MessageExceptionMixin):
    """
    The object / Document being searched for does not exist.
    """
