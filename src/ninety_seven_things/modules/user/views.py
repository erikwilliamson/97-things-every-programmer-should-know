# Standard Library Imports
import logging
import uuid
from typing import List, Optional

# 3rd-Party Imports
from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException, Query
from icecream import ic
from pydantic import EmailStr
from starlette import status

# Application-Local Imports
from wj.core.config import settings
from wj.lib.exceptions import DoesNotExistException
from wj.lib.security import auth_backend
from wj.modules.user import dependencies as user_dependencies
from wj.modules.user import schemas as user_schemas
from wj.modules.user import service as user_service

# Local Folder Imports
from .exceptions import UserExistsException
from .role import allow_create_anonymous_user, allow_impersonate_user, allow_list_user, allow_view_user
from .service import create_user, find_user, get_many, get_many_by_email

router = APIRouter()
logger = logging.getLogger(settings.LOG_NAME)


@router.get(
    path="/user/{user_id}/impersonate",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(allow_impersonate_user)],
    summary="Impersonates a User",
)
async def impersonate(user: user_dependencies.UserIDDependency) -> user_schemas.ImpersonationResponse:
    strategy = auth_backend.get_strategy()
    token = await strategy.write_token(user)

    return user_schemas.ImpersonationResponse(access_token=token, token_type="bearer", impersonator=user.id)


@router.get(
    path="/user/me/roles",
    status_code=status.HTTP_200_OK,
    summary="Retrieves the Current User's Roles",
)
async def get_my_roles(user_roles: user_dependencies.UserRoleDependency) -> user_schemas.UserRoles:
    return user_roles


@router.get(
    path="/user/{user_id}/roles",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(allow_view_user)],
    summary="Retrieves a User's Roles",
)
async def get_user_roles(
    # user: user_models.User = Depends(security.current_active_user),
    user: user_dependencies.UserIDDependency,
) -> user_schemas.UserRoles:
    return await user_service.get_roles(user_id=user.id)


# @router.get(
#     path="/user/{user_id}/cart",
#     status_code=status.HTTP_200_OK,
#     dependencies=[Depends(allow_view_user)],
#     summary="Retrieves a User's Cart",
# )
# async def get_user_cart(
#     user: user_dependencies.UserIDDependency,
# ) -> cart_schemas.CartView:
#     try:
#         cart = await cart_service.get_by_user_id(user_id=user.id)
#     except DoesNotExistException as exc:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=exc.message,
#         ) from exc
#
#     return cart_schemas.CartView(**cart.model_dump())


@router.get(
    path="/user/find",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(allow_view_user)],
    summary="Searches for a user",
)
async def find(
    user_id: Optional[PydanticObjectId] = None,
    email: Optional[EmailStr] = None,
    phone_number: Optional[str] = None,
) -> user_schemas.UserView:
    if [v is not None for v in locals().values()].count(True) != 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="One and only one of user_id, email, or phone_number can be specified",
        )

    try:
        user = await find_user(user_id=user_id, email=email, phone_number=phone_number)
    except DoesNotExistException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc

    return user_schemas.UserView(**user.model_dump())


@router.get(
    path="/user/find_many",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(allow_view_user)],
    summary="Searches for a number of users",
)
async def find_many(email_addresses: list[EmailStr] | None = Query(default=None)) -> List[user_schemas.UserView]:
    try:
        users = await get_many_by_email(email_addresses=email_addresses)
    except DoesNotExistException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc

    return [user_schemas.UserView(**user.model_dump()) for user in users]


@router.get(
    path="/user",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(allow_list_user)],
    summary="Retrieves all Users",
)
async def read_all_users(skip: int = 0, limit: int = 100) -> List[user_schemas.UserView]:
    return [user_schemas.UserView(**user.model_dump()) for user in await get_many(skip=skip, limit=limit)]


@router.post(
    path="/user",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(allow_create_anonymous_user)],
    summary="Create an Anonymous User",
)
async def create_anonymous_user(
    user_in: user_schemas.AnonymousUserCreate,
) -> user_schemas.UserView:
    logger.info(f"Creating user: {user_in.email} initiated by {user_in.email}")

    user_details = user_in.model_dump()

    user_details["is_anonymous"] = True
    user_details["password"] = str(uuid.uuid4())
    user_details["is_active"] = False
    user_details["is_superuser"] = False
    user_details["is_verified"] = False

    try:
        created_user = await create_user(user_schemas.UserCreate(**user_details))
    except UserExistsException as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message) from exc

    logger.info(f"User {user_in.email} created with ID {created_user.id}")

    user_view = created_user.model_dump()
    user_view["registered_account"] = None

    return user_schemas.UserView(**user_view)


@router.post(
    path="/user/associate",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(allow_create_anonymous_user)],
    summary="Associates an anonymous user account with a registered account",
)
async def associate_anonymous_account_with_registered_account(
    anonymous_user_id: PydanticObjectId,
    registered_user_id: PydanticObjectId,
) -> user_schemas.UserView:
    anonymous_user = await user_service.get_one_by_id(user_id=anonymous_user_id)
    registered_user = await user_service.get_one_by_id(user_id=registered_user_id)
    ic(anonymous_user, registered_user)

    anonymous_user.registered_account = registered_user
    await anonymous_user.save()

    ic(registered_user.model_dump())
    registered_user_data = registered_user.model_dump()
    registered_user_data["unregistered_accounts"] = [
        unregistered_account.model_dump() for unregistered_account in registered_user.unregistered_accounts
    ]
    # return user_schemas.UserView(**registered_user.model_dump())
    return user_schemas.UserView(**registered_user_data)
