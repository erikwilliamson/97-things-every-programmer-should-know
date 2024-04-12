# Standard Library Imports
from dataclasses import dataclass

# Application-Local Imports
from wj.lib.exceptions import APIException, MessageExceptionMixin


@dataclass
class MailException(APIException, MessageExceptionMixin):
    pass
