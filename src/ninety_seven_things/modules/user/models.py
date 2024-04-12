# Future Imports
from __future__ import annotations

# Standard Library Imports
from typing import ClassVar, Dict, Optional

# 3rd-Party Imports
from beanie import Document, Link
from fastapi_users_db_beanie import BeanieBaseUser, BeanieUserDatabase

# Application-Local Imports
from ninety_seven_things.lib import enums, types


class User(BeanieBaseUser, Document):
    """
    Users
    """

    given_name: str
    family_name: Optional[str] = None
    phone_number: types.PhoneNumber

    authorization_fields: ClassVar[Dict[enums.Role, Optional[str]]] = {enums.Role.SELF: None}


async def get_user_db() -> BeanieUserDatabase:
    yield BeanieUserDatabase(User)
