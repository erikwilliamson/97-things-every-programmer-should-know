# Standard Library Imports
from typing import Annotated

# 3rd-Party Imports
from beanie import PydanticObjectId
from fastapi import Depends, status
from fastapi.exceptions import HTTPException

# Application-Local Imports
from ninety_seven_things.lib.exceptions import DoesNotExistException

# Local Folder Imports
from .models import Article
from .service import get_by_id


async def valid_article_id(article_id: PydanticObjectId) -> Article:
    try:
        company = await get_by_id(article_id=article_id, fetch_links=True)
    except DoesNotExistException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc

    return company


ArticleDependency = Annotated[Article, Depends(valid_article_id)]
