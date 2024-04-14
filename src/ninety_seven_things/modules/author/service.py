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
from .exceptions import AuthorDoesNotExistException, AuthorException
from .models import Author
from .schemas import AuthorCreate, AuthorUpdate

logger = logging.getLogger(settings.LOG_NAME)


async def get_by_name(name: str, fetch_links: bool = False) -> Author:
    author = await Author.find_one(Author.name == name, fetch_links=fetch_links)

    if author is None:
        raise AuthorDoesNotExistException(message=f"An author with the name {name} does not exist")

    return author


async def get_by_id(author_id: PydanticObjectId, fetch_links: bool = False) -> Author:
    author = await Author.find_one(Author.id == author_id, fetch_links=fetch_links)

    if author is None:
        raise DoesNotExistException(message=f"An author with id {author_id} does not exist")

    return author


async def get_many(fetch_links: bool = False, skip: int = 0, limit: int = 100) -> List[Author]:
    """ "
    Retrieve many authors
    """
    try:
        return await Author.find_all(fetch_links=fetch_links).sort(+Author.name).skip(skip).limit(limit).to_list()
    except ValidationError as exc:
        raise AuthorException(message=f"{str(exc)}") from exc


async def create(author_in: AuthorCreate) -> Author:
    """
    Creates an author
    """
    author = author_in.model_dump()

    created_author = Author(**author)
    await created_author.save()

    return created_author


async def update(author: Author, updated_author_in: AuthorUpdate) -> Author:
    """
    Update an Author
    """

    updated_author_data = updated_author_in.model_dump(exclude_unset=True)

    for key, value in updated_author_data.items():
        setattr(author, key, value)

    await author.save()

    return author


async def delete_one(author: Author) -> None:
    await author.delete()
    return


async def delete_by_id(author_id: PydanticObjectId) -> None:
    author = await get_by_id(author_id=author_id)
    await delete_one(author)
    return


async def delete_all() -> None:
    await Author.delete_all()
    return
