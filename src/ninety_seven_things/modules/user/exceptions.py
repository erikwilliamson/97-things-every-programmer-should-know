# Standard Library Imports
from dataclasses import dataclass

# Application-Local Imports
from wj.lib.exceptions import APIException, KeysExceptionMixin, MessageExceptionMixin


@dataclass
class UserException(APIException):
    pass


@dataclass
class UserDoesNotExistException(UserException, KeysExceptionMixin):
    pass


@dataclass
class UserExistsException(UserException, MessageExceptionMixin):
    pass
