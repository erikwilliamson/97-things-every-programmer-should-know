# Standard Library Imports
import logging
from typing import List

# 3rd-Party Imports
from beanie import PydanticObjectId
from pydantic import ValidationError

# Application-Local Imports
from ninety_seven_things.core.config import settings
from ninety_seven_things.lib.exceptions import DoesNotExistException

# Local Folder Imports
from .exceptions import ArticleDoesNotExistException, ArticleException, ArticleValidationException
from .models import Article
from .schemas import AbridgedArticleProjection, ArticleCreate, ArticleUpdate

logger = logging.getLogger(settings.LOG_NAME)


async def get_by_index_and_language(index: int, language: str) -> Article:
    article = await Article.find_one(Article.index == index, Article.language == language)

    if article is None:
        raise DoesNotExistException(message=f"An article with index {index} and language {language} does not exist")

    return article


async def get_by_id(article_id: PydanticObjectId, fetch_links: bool = False) -> Article:
    article = await Article.find_one(Article.id == article_id, fetch_links=fetch_links)

    if article is None:
        raise DoesNotExistException(message=f"An article with id {article_id} does not exist")

    return article


async def get_by_language(language: str) -> List[AbridgedArticleProjection]:
    articles = (
        await Article.find(Article.language == language)
        .sort(+Article.index)
        .project(AbridgedArticleProjection)
        .to_list()
    )

    if articles is []:
        raise DoesNotExistException(message=f"Unable to locate articles with language {language}")

    return articles


async def get_all(fetch_links: bool = False, skip: int = 0, limit: int = 100) -> List[Article]:
    """ "
    Retrieve many articles
    """
    try:
        return (
            await Article.find_all(fetch_links=fetch_links)
            .sort(+Article.index, +Article.language)
            .skip(skip)
            .limit(limit)
            .to_list()
        )
    except ValidationError as exc:
        raise ArticleValidationException(message=f"{str(exc)}") from exc


async def create(article_in: ArticleCreate) -> Article:
    """
    Creates an article
    """

    created_article = Article(**article_in.model_dump())
    await created_article.save()

    return created_article


async def update(article: Article, updated_article_in: ArticleUpdate) -> Article:
    """
    Update a Article
    """

    updated_article_data = updated_article_in.model_dump(exclude_unset=True)

    for key, value in updated_article_data.items():
        setattr(article, key, value)

    await article.save()

    return article


async def delete_one(article: Article) -> None:
    await article.delete()

    return


async def delete_by_id(article_id: PydanticObjectId) -> None:
    article = await get_by_id(article_id=article_id)

    await delete_one(article)

    return


async def delete_all() -> None:
    await Article.delete_all()
    return
