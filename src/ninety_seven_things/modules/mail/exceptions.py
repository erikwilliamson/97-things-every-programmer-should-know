# Standard Library Imports
from dataclasses import dataclass

# Application-Local Imports
from ninety_seven_things.lib.exceptions import NinetySevenThingsException, MessageExceptionMixin


@dataclass
class MailException(NinetySevenThingsException, MessageExceptionMixin):
    pass

