# Standard Library Imports
import json
import logging
import pathlib
import random

# 3rd-Party Imports
from fastapi import APIRouter, BackgroundTasks, Depends, Response, status
from fastapi.exceptions import HTTPException

# Application-Local Imports
from ninety_seven_things.core.config import settings
from ninety_seven_things.modules.article import models as article_models
from ninety_seven_things.modules.article import schemas as article_schemas
from ninety_seven_things.modules.article import service as article_service
from ninety_seven_things.modules.author import models as author_models
from ninety_seven_things.modules.author import schemas as author_schemas
from ninety_seven_things.modules.author import service as author_service
from ninety_seven_things.modules.user import dependencies as user_dependencies
from ninety_seven_things.modules.user import exceptions as user_exceptions
from ninety_seven_things.modules.user import models as user_models
from ninety_seven_things.modules.user import schemas as user_schemas
from ninety_seven_things.modules.user import service as user_service
from ninety_seven_things.modules.utilities import service as utilities_service

# Local Folder Imports
from .role import allow_reseed_db, allow_wipe_db
from .schemas import LoadedDataReport
from .service import clear_db, insert_erik, load_seed_data

router = APIRouter()
logger = logging.getLogger(settings.LOG_NAME)


@router.post(
    path="/erik",
    status_code=status.HTTP_201_CREATED,
    summary="Creates Erik",
    responses={
        status.HTTP_201_CREATED: {
            "content": {"application/json": {"schema": {"title": "Fooooo"}}},
        }
    },
)
async def erik() -> Response:
    await insert_erik()
    return Response(status_code=status.HTTP_201_CREATED)


@router.post(
    path="/load_seed_data",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(allow_reseed_db)],
    summary="Loads Seed Data",
)
async def load_seed_data(
    user_roles: user_dependencies.UserRoleDependency,
    wipe: bool = True,
) -> LoadedDataReport:
    return await utilities_service.load_seed_data(wipe=wipe)


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
        article_models.Article,
        user_models.User,
    ]

    for model in models:
        logger.warning(f"Deleting all {model.__name__} documents")
        await model.delete_all()
