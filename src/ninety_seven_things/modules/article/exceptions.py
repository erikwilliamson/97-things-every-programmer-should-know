# Application-Local Imports
from ninety_seven_things.lib.exceptions import MessageException


class ArticleException(MessageException):
    pass


class ArticleDoesNotExistException(ArticleException):
    pass
