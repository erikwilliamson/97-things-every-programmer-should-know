from dataclasses import dataclass

# Application-Local Imports
from ninety_seven_things.lib.exceptions import NinetySevenThingsException, MessageException


@dataclass
class AuthorException(NinetySevenThingsException, MessageException):
    pass


@dataclass
class AuthorDoesNotExistException(AuthorException):
    pass
