# Standard Library Imports
import logging
from typing import Optional

# 3rd-Party Imports
from beanie import PydanticObjectId
from pydantic import AnyHttpUrl

# Application-Local Imports
from ninety_seven_things.core.config import settings
from ninety_seven_things.lib import schemas

logger = logging.getLogger(settings.LOG_NAME)


class FullAuthorView(schemas.Entity):
    id: PydanticObjectId
    given_name: str
    family_name: Optional[str] = None
    full_name: str
    url: AnyHttpUrl


class AbridgedAuthorView(schemas.Entity):
    id: PydanticObjectId
    full_name: str


class AuthorCreate(schemas.Entity):
    given_name: str
    family_name: Optional[str] = None
    url: AnyHttpUrl


class AuthorUpdate(schemas.Entity):
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    url: Optional[AnyHttpUrl] = None
