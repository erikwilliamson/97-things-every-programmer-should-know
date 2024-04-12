# Future Imports
from __future__ import annotations

# Standard Library Imports
from typing import ClassVar, Dict, Optional

# 3rd-Party Imports
from beanie import Document, Link
from fastapi_users_db_beanie import BeanieBaseUser, BeanieUserDatabase

# Application-Local Imports
from wj.lib import enums, types


class User(BeanieBaseUser, Document):
    """
    Users
    """

    given_name: str
    family_name: Optional[str] = None
    phone_number: types.PhoneNumber
    stripe_customer_id: Optional[str] = None
    is_anonymous: bool = False
    registered_account: Optional[Link[User]] = None

    # unregistered_accounts: List[Link["User"]] = Field(default_factory=list)
    # registered_account: Optional[Link["User"]] = None

    # address: address_schemas.Address

    authorization_fields: ClassVar[Dict[enums.Role, Optional[str]]] = {enums.Role.SELF: None}


async def get_user_db() -> BeanieUserDatabase:
    yield BeanieUserDatabase(User)
