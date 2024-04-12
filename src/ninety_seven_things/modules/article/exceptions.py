# Application-Local Imports
from ninety_seven_things.lib.exceptions import NinetySevenThingsException


class ArticleException(NinetySevenThingsException):
    pass


class ArticleDoesNotExistException(ArticleException):
    pass
