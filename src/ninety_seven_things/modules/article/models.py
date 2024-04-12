# Standard Library Imports
import logging

# 3rd-Party Imports
from beanie import Document, Indexed

# Application-Local Imports
from ninety_seven_things.core.config import settings


logger = logging.getLogger(settings.LOG_NAME)


class Article(Document):
    title: Indexed(str)
    contents: str
    language: str
