# Standard Library Imports
from dataclasses import dataclass

# Application-Local Imports
from ninety_seven_things.lib.exceptions import MessageExceptionMixin, NinetySevenThingsException


@dataclass
class AuthorException(NinetySevenThingsException, MessageExceptionMixin):
    pass


@dataclass
class AuthorDoesNotExistException(AuthorException):
    pass
