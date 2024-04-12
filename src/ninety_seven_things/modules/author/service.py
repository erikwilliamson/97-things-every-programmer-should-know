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
from .exceptions import ArticleException, ArticleDoesNotExistException
from .models import Article
from .schemas import ArticleCreate, ArticleUpdate

logger = logging.getLogger(settings.LOG_NAME)


async def get_by_name(name: str, fetch_links: bool = False) -> Article:
    article = await Article.find_one(Article.name == name, fetch_links=fetch_links)

    if article is None:
        raise ArticleDoesNotExistException(message=f"An article with the name {name} does not exist")

    return article


async def get_by_id(article_id: PydanticObjectId, fetch_links: bool = False) -> Article:
    article = await Article.find_one(Article.id == article_id, fetch_links=fetch_links)

    if article is None:
        raise DoesNotExistException(message=f"An article with id {article_id} does not exist")

    return article


async def get_many(fetch_links: bool = False, skip: int = 0, limit: int = 100) -> List[Article]:
    """ "
    Retrieve many articles
    """
    try:
        return await Article.find_all(fetch_links=fetch_links).sort(+Article.name).skip(skip).limit(limit).to_list()
    except ValidationError as exc:
        raise ArticleException(message=f"{str(exc)}") from exc


async def create(company_in: ArticleCreate) -> Article:
    """
    Creates an article
    """
    company = company_in.model_dump()

    # ic(company)
    created_company = Company(**company)
    await created_company.save()

    try:
        return await get_by_id(company_id=created_company.id, fetch_links=True)
    except DoesNotExistException as exc:
        raise CompanyException(message=f"Unable to retrieve company: {str(exc)}") from exc


async def update(company: Company, updated_company_in: CompanyUpdate) -> Company:
    """
    Update a Company
    """

    updated_company_data = updated_company_in.model_dump(exclude_unset=True)

    for key, value in updated_company_data.items():
        setattr(company, key, value)

    await company.save()

    return company


async def delete_one(company: Company) -> None:

    await company.delete()

    return


async def delete_by_id(company_id: PydanticObjectId) -> None:
    company = await get_by_id(company_id=company_id)

    await delete_one(company)

    return


async def delete_all() -> None:
    await Company.delete_all()
    return
