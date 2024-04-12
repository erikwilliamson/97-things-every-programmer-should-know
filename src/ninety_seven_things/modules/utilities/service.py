# Standard Library Imports
import json
import logging
import pathlib
import random
from datetime import datetime, UTC

# 3rd-Party Imports
from fastapi import APIRouter, Depends, Response, status
from fastapi.exceptions import HTTPException
from git import Repo

# Application-Local Imports
from ninety_seven_things.core.config import settings
from ninety_seven_things.lib import constants
from ninety_seven_things.modules.author import schemas as author_schemas
from ninety_seven_things.modules.author import service as author_service
from ninety_seven_things.modules.author import models as author_models
from ninety_seven_things.modules.article import schemas as article_schemas
from ninety_seven_things.modules.article import service as article_service
from ninety_seven_things.modules.article import models as article_models
from ninety_seven_things.modules.user import dependencies as user_dependencies
from ninety_seven_things.modules.user import exceptions as user_exceptions
from ninety_seven_things.modules.user import models as user_models
from ninety_seven_things.modules.user import schemas as user_schemas
from ninety_seven_things.modules.user import service as user_service
from ninety_seven_things.modules.application_administrator import models as application_administrator_models
from ninety_seven_things.lib.types.phone_number import PhoneNumber

# Local Folder Imports
from .role import allow_reseed_db, allow_wipe_db
from .schemas import LoadedDataReport

router = APIRouter()
logger = logging.getLogger(settings.LOG_NAME)


async def insert_erik() -> application_administrator_models.ApplicationAdministrator:
    erik = await user_service.create_user(
        user_in=user_schemas.UserCreate(
            given_name="Erik",
            family_name="Williamson",
            email="erik@techsanity.ca",
            password="asdf",
            phone_number=PhoneNumber("2125551212"),
            is_active=True,
            is_verified=True,
            is_superuser=True
        )
    )
    return erik

async def load_seed_data(
    wipe: bool = True,
) -> LoadedDataReport:
    timestamp = datetime.now(UTC).strftime(constants.TIMESTAMP_FORMAT)
    repo_dir = pathlib.Path(f"{settings.SOURCE_REPO_URL}{timestamp}")

    if wipe:
        logger.info("Wiping DB")
        await clear_db()

    Repo.clone_from(settings.SOURCE_REPO_URL, repo_dir)

    created_authors = []
    created_articles = []

    return LoadedDataReport(
        authors=created_authors,
        articles=created_articles
    )


@router.delete(
    path="/wipe",
    response_class=Response,
    dependencies=[Depends(allow_wipe_db)],
    summary="Deletes everything",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def clear_db():
    """
    delete (pretty much) everything
    """

    models = [
        author_models.Author,
        article_models.Article
    ]

    for model in models:
        logger.warning(f"Deleting all {model.__name__} documents")
        await model.delete_all()
