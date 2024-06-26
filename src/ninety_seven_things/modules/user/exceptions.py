# Standard Library Imports
from dataclasses import dataclass

# Application-Local Imports
from ninety_seven_things.lib.exceptions import MessageExceptionMixin, NinetySevenThingsException


@dataclass
class UserException(NinetySevenThingsException):
    pass


@dataclass
class UserDoesNotExistException(UserException):
    pass


@dataclass
class UserExistsException(UserException, MessageExceptionMixin):
    pass
