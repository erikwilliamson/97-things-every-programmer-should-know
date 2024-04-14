# Standard Library Imports
import logging
from typing import Optional

# 3rd-Party Imports
from beanie import PydanticObjectId
from pydantic import BaseModel

# Application-Local Imports
from ninety_seven_things.core.config import settings
from ninety_seven_things.lib import schemas

logger = logging.getLogger(settings.LOG_NAME)


class FullArticleView(schemas.Entity):
    id: PydanticObjectId
    title: str
    index: int
    contents: str
    language: str


class AbridgedArticleView(schemas.Entity):
    id: PydanticObjectId
    title: str
    index: int


class AbridgedArticleProjection(BaseModel):
    _id: PydanticObjectId
    title: str
    index: int


class ArticleCreate(schemas.Entity):
    title: str
    index: int
    contents: str
    language: str


class ArticleUpdate(schemas.Entity):
    title: Optional[str]
    contents: Optional[str]
