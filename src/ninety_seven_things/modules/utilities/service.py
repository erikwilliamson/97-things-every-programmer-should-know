# Standard Library Imports
import json
import logging
import pathlib
import random
from datetime import UTC, datetime

# 3rd-Party Imports
from fastapi import APIRouter, Depends, Response, status
from fastapi.exceptions import HTTPException
from git import Repo

# Application-Local Imports
from ninety_seven_things.core.config import settings
from ninety_seven_things.lib import constants
from ninety_seven_things.lib.types.phone_number import PhoneNumber
from ninety_seven_things.modules.article import models as article_models
from ninety_seven_things.modules.article import schemas as article_schemas
from ninety_seven_things.modules.article import service as article_service
from ninety_seven_things.modules.author import models as author_models
from ninety_seven_things.modules.user import models as user_models
from ninety_seven_things.modules.user import schemas as user_schemas
from ninety_seven_things.modules.user import service as user_service
from ninety_seven_things.modules.git import interface as git_interface

# Local Folder Imports
from .role import allow_reseed_db, allow_wipe_db
from .schemas import LoadedDataReport

router = APIRouter()
logger = logging.getLogger(settings.LOG_NAME)


async def insert_erik() -> user_models.User:
    erik = await user_service.create_user(
        user_in=user_schemas.UserCreate(
            given_name="Erik",
            family_name="Williamson",
            email="erik@techsanity.ca",
            password="asdf",
            phone_number=PhoneNumber("2125551212"),
            is_active=True,
            is_verified=True,
            is_superuser=True,
        )
    )
    return erik


async def load_seed_data(
    wipe: bool = True,
) -> LoadedDataReport:
    created_authors = []
    created_articles = []

    logger.info(f"Loading seed data from {settings.SOURCE_REPO_URL}")

    logger.info(f"Instantiating git interface")
    git = git_interface.Git()

    if wipe:
        logger.info("Wiping DB")
        await clear_db()

    await git.clone_repo()

    for language in constants.SUPPORTED_LANGUAGES:
        with open(git.local_dir / language / "README.md") as f:
            contents = f.read()

            article_in = article_schemas.ArticleCreate(
                title="README",
                index=0,
                contents=contents,
                language=language,
            )

            article = await article_service.create(article_in=article_in)

            created_articles.append(article.id)

        for i in range(constants.FIRST_ARTICLE_ID, constants.LAST_ARTICLE_ID + 1):
            with open(git.local_dir / language / f"thing_{i:02}" / "README.md") as f:
                raw_article_data = f.read()
                _, _, title = raw_article_data.split("\n")[0].partition(" ")

                contents = "\n".join(raw_article_data.split("\n")[2:])

                article_in = article_schemas.ArticleCreate(
                    title=title,
                    index=i,
                    contents=contents,
                    language=language,
                )

                article = await article_service.create(article_in=article_in)

                created_articles.append(article.id)

    return LoadedDataReport(authors=created_authors, articles=created_articles)


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

    models = [author_models.Author, article_models.Article]

    for model in models:
        logger.warning(f"Deleting all {model.__name__} documents")
        await model.delete_all()
