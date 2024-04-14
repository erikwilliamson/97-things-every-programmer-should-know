# Standard Library Imports
from dataclasses import dataclass

# Application-Local Imports
from ninety_seven_things.lib.exceptions import MessageExceptionMixin, NinetySevenThingsException


@dataclass
class GitException(NinetySevenThingsException):
    pass


@dataclass
class CloneRepoException(GitException, MessageExceptionMixin):
    pass
