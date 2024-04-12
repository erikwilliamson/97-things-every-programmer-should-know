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
class MessageException:
    message: str


class ConfigurationException(NinetySevenThingsException):
    """
    Configuration Error
    """
