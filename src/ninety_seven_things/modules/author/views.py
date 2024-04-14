# Standard Library Imports
import logging
from typing import List

# 3rd-Party Imports
from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import ValidationError

# Application-Local Imports
from ninety_seven_things.core.config import settings
from ninety_seven_things.lib import exceptions, schemas, security
from ninety_seven_things.modules.user import dependencies as user_dependencies
from ninety_seven_things.modules.user import models as user_models

# Local Folder Imports
from .dependencies import AuthorDependency
from .exceptions import AuthorDoesNotExistException, AuthorException
from .role import allow_delete_all_author, allow_delete_author, allow_update_author, allow_view_author
from .schemas import AbridgedAuthorView, AuthorCreate, AuthorUpdate, FullAuthorView
from .service import create, delete_all, delete_one, get_many, update

router = APIRouter()
logger = logging.getLogger(settings.LOG_NAME)


@router.post(
    path="/author",
    status_code=status.HTTP_201_CREATED,
    summary="Create an Author",
)
async def create_author(
    author_in: AuthorCreate,
) -> FullAuthorView:
    logger.info(f"Creating author: {author_in.name}")

    try:
        created_author = await create(author_in=author_in)
    except AuthorException as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message) from exc

    logger.info(f"Author {author_in.name} created with ID {created_author.id}")

    return FullAuthorView(**created_author.dict())


@router.get(
    path="/author",
    status_code=status.HTTP_200_OK,
    summary="Retrieve all Authors",
)
async def read_all_authors(
    skip: int = 0,
    limit: int = 100,
) -> List[FullAuthorView]:
    try:
        authors = await get_many(fetch_links=True, skip=skip, limit=limit)
    except ValidationError as exc:
        raise exceptions.DataIntegrityException(source_exception=exc) from exc

    return [FullAuthorView(**author.dict()) for author in authors]


@router.get(
    path="/author/{author_id}",
    status_code=status.HTTP_200_OK,
    summary="Retrieve one Author",
)
async def read_one_author(author: AuthorDependency) -> FullAuthorView:
    return FullAuthorView(**author.model_dump())


@router.patch(
    path="/author/{author_id}",
    dependencies=[Depends(allow_update_author)],
    summary="Update a Author",
)
async def update_author(
    user_roles: user_dependencies.UserRoleDependency,
    author: AuthorDependency,
    updated_author_in: AuthorUpdate,
) -> FullAuthorView:
    logger.info(f"Updating author {author.name}")

    try:
        updated_author = await update(author=author, updated_author_in=updated_author_in)
    except AuthorException as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message) from exc

    return FullAuthorView(**updated_author.model_dump())


@router.delete(
    path="/author/{author_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    dependencies=[Depends(allow_delete_author)],
    summary="Delete a Author",
)
async def delete_one_author(author: AuthorDependency, user: user_models.User = Depends(security.current_active_user)):
    logger.info(f"Deleting author ({author.id}) {author.name} initiated by {user.email}")
    await delete_one(author=author)


@router.delete(
    path="/author",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    dependencies=[Depends(allow_delete_all_author)],
    summary="Delete all Authors",
)
async def delete_all_authors(user: user_models.User = Depends(security.current_active_user)):
    logger.info(f"Deleting all authors initiated by {user.email}")
    await delete_all()
    return
