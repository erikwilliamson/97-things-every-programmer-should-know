# Standard Library Imports
import logging
from typing import List

# 3rd-Party Imports
from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import ValidationError

# Application-Local Imports
from ninety_seven_things.core.config import settings
from ninety_seven_things.lib import exceptions, security
from ninety_seven_things.modules.user import models as user_models

# Local Folder Imports
from .dependencies import ArticleDependency
from .exceptions import ArticleException
from .role import (
    allow_create_article,
    allow_delete_all_article,
    allow_delete_article,
    allow_list_article,
    allow_update_article,
)
from .schemas import ArticleCreate, ArticleUpdate, FullArticleView
from .service import create, delete_all, delete_one, get_all, update

router = APIRouter()
logger = logging.getLogger(settings.LOG_NAME)


@router.post(
    path="/article",
    status_code=status.HTTP_201_CREATED,
    summary="Create an Article",
)
async def create_article(
    article_in: ArticleCreate,
) -> FullArticleView:
    logger.info(f"Creating article: {article_in.name}")

    try:
        created_article = await create(article_in=article_in)
    except ArticleException as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message) from exc

    logger.info(f"Article {article_in.name} created with ID {created_article.id}")

    return FullArticleView(**created_article.dict())


@router.get(
    path="/article",
    status_code=status.HTTP_200_OK,
    summary="Retrieve all Articles",
)
async def read_all_articles(
    skip: int = 0,
    limit: int = 100,
) -> List[FullArticleView]:
    try:
        articles = await get_all(fetch_links=True, skip=skip, limit=limit)
    except ValidationError as exc:
        raise exceptions.DataIntegrityException(source_exception=exc) from exc

    return [FullArticleView(**article.dict()) for article in articles]


@router.get(
    path="/article/{article_id}",
    status_code=status.HTTP_200_OK,
    summary="Retrieve one Article",
)
async def read_one_article(
    article: ArticleDependency,
) -> FullArticleView:
    return FullArticleView(**article.model_dump())


@router.patch(
    path="/article/{article_id}",
    dependencies=[Depends(allow_update_article)],
    summary="Update an Article",
)
async def update_article(
    article: ArticleDependency,
    updated_article_in: ArticleUpdate,
) -> FullArticleView:
    logger.info(f"Updating article {article.name}")

    try:
        updated_article = await update(
            article=article,
            updated_article_in=updated_article_in,
        )
    except ArticleException as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message) from exc

    return FullArticleView(**updated_article.model_dump())


@router.delete(
    path="/article/{article_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    dependencies=[Depends(allow_delete_article)],
    summary="Delete an Article",
)
async def delete_one_article(
    article: ArticleDependency, user: user_models.User = Depends(security.current_active_user)
):
    logger.info(f"Deleting article ({article.id}) {article.name} initiated by {user.email}")
    await delete_one(article=article)


@router.delete(
    path="/article",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    dependencies=[Depends(allow_delete_all_article)],
    summary="Delete all Articles",
)
async def delete_all_articles(user: user_models.User = Depends(security.current_active_user)):
    logger.info(f"Deleting all articles initiated by {user.email}")
    await delete_all()
    return
