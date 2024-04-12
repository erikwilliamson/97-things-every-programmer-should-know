# Standard Library Imports
from typing import Annotated

# 3rd-Party Imports
from beanie import PydanticObjectId
from fastapi import Depends, status
from fastapi.exceptions import HTTPException
from icecream import ic
from pydantic import EmailStr

# Application-Local Imports
from wj.lib import security
from wj.lib.exceptions import DoesNotExistException

# Local Folder Imports
from .models import User
from .schemas import UserRoles
from .service import get_one_by_email, get_one_by_id, get_roles


async def valid_user_id(user_id: PydanticObjectId) -> User:
    try:
        user = await get_one_by_id(user_id, fetch_links=True)
    except DoesNotExistException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc

    return user


async def valid_user_email(user_email: EmailStr | str) -> User:
    try:
        user = await get_one_by_email(email=user_email)
    except DoesNotExistException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc

    return user


async def user_roles(
    current_user: User = Depends(security.current_active_user),
) -> UserRoles:
    if current_user is None:
        ic("current_user is None")
        return UserRoles()

    roles = await get_roles(user_id=current_user.id)
    return roles


UserIDDependency = Annotated[User, Depends(valid_user_id)]
UserEmailDependency = Annotated[User, Depends(valid_user_email)]
UserRoleDependency = Annotated[UserRoles, Depends(user_roles)]
