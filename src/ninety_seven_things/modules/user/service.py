# Standard Library Imports
import logging
from typing import List, Optional, Type

# 3rd-Party Imports
from beanie import PydanticObjectId
from beanie.operators import In
from icecream import ic
from pydantic import EmailStr

# Application-Local Imports
from ninety_seven_things.core.config import settings
from ninety_seven_things.lib import exceptions, passwords

# Local Folder Imports
from .exceptions import UserDoesNotExistException, UserExistsException
from .models import User
from .schemas import UserCreate, UserRoles

logger = logging.getLogger(settings.LOG_NAME)


async def create_user(user_in: UserCreate) -> User:
    try:
        await get_one_by_email(email=user_in.email)
    except UserDoesNotExistException:
        pass
    else:
        raise UserExistsException(f"A user with email {user_in.email} already exists")

    # Convert the supplied user object to a dict so that we can massage it
    temp_user = user_in.model_dump(exclude={"password"})

    # add the hashed password
    temp_user["hashed_password"] = passwords.hash_password(user_in.password)

    # now create the proper user object
    created_user = User(**temp_user)

    await created_user.save()

    return created_user


async def get_many(fetch_links: bool = False, skip: int = 0, limit: int = 100) -> List[User]:
    """ "
    Retrieve many Users
    """
    return await User.find_all(fetch_links=fetch_links).skip(skip).limit(limit).to_list()


async def get_one_by_id(user_id: PydanticObjectId, fetch_links: bool = False) -> User:
    """ "
    Retrieve many Users
    """
    user = await User.find_one(User.id == user_id, fetch_links=fetch_links)

    if user is None:
        raise UserDoesNotExistException

    return user


async def get_one_by_email(email: EmailStr | str) -> User:
    target_user = await User.find_one(User.email == email)

    if target_user is None:
        raise UserDoesNotExistException

    return target_user


async def get_roles(user_id: PydanticObjectId) -> UserRoles:
    user = await get_one_by_id(user_id=user_id)

    roles = {
        "user_id": user_id,
        "application_administrator": user.is_superuser,
    }
    return UserRoles(**roles)
