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
from .schemas import UserCreate

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


async def get_many_by_email(email_addresses: List[EmailStr]) -> List[User]:
    email_addresses = [e.lower() for e in email_addresses]
    result = await User.find(In(User.email, email_addresses)).to_list()
    missing = set(email_addresses).difference({u.email for u in result})

    if len(result) != len(email_addresses):
        raise UserDoesNotExistException

    return result


async def get_many_by_id(ids: List[PydanticObjectId]) -> List[User]:
    result = await User.find(In(User.id, ids)).to_list()
    missing = set(ids).difference({u.email for u in result})

    if len(result) != len(ids):
        raise exceptions.DoesNotExistException(
            message=f"One or more ids requested do not exist: {missing}",
        )

    return result


async def get_all_non_admin_users() -> List[User]:
    # Gets all for now... we'll need to filter this down later
    return await User.find_all().to_list()


async def find_user(
    user_id: Optional[PydanticObjectId] = None,
    email: Optional[EmailStr] = None,
    phone_number: Optional[str] = None,
) -> User:
    if user_id:
        user = await User.find_one(User.id == user_id)
    elif email:
        user = await User.find_one({"email": {"$regex": f"^{email}$", "$options": "i"}})
    elif phone_number:
        user = await User.find_one(User.phone_number == phone_number)
    else:
        raise ValueError("One of user_id, email, or phone_number must be specified")

    if user is None:
        raise exceptions.DoesNotExistException(message="a user with matching the criteria provided does not exist")

    return user


async def associate_anonymous_account(
    anonymous_user_id: PydanticObjectId,
    registered_user_id: PydanticObjectId,
) -> bool:
    anonymous_user = await get_one_by_id(user_id=anonymous_user_id)
    registered_user = await get_one_by_id(user_id=registered_user_id)

    ic(anonymous_user, registered_user)

    anonymous_user.registered_account = registered_user
    await anonymous_user.save()

    # ic(registered_user.model_dump())
    # registered_user_data = registered_user.model_dump()
    # registered_user_data["unregistered_accounts"] = [
    #     unregistered_account.model_dump() for unregistered_account in registered_user.unregistered_accounts
    # ]
    # # return user_schemas.UserView(**registered_user.model_dump())
    # return user_schemas.UserView(**registered_user_data)

    return True
