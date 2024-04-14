# Standard Library Imports
from dataclasses import dataclass

# Application-Local Imports
from ninety_seven_things.lib.exceptions import MessageExceptionMixin, NinetySevenThingsException


@dataclass
class ArticleException(NinetySevenThingsException):
    pass


@dataclass
class ArticleDoesNotExistException(ArticleException):
    pass


@dataclass
class ArticleValidationException(ArticleException, MessageExceptionMixin):
    pass
