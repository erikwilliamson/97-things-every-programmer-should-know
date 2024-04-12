# Future Imports
from __future__ import annotations

# Standard Library Imports
import logging
from typing import Optional

# 3rd-Party Imports
from beanie import PydanticObjectId
from fastapi_users import schemas
from pydantic import BaseModel, EmailStr, field_validator

# Application-Local Imports
from ninety_seven_things.core.config import settings
from ninety_seven_things.lib import types
from ninety_seven_things.lib.types.phone_number import PhoneNumber

logger = logging.getLogger(settings.LOG_NAME)


class UserCreate(schemas.BaseUserCreate):
    given_name: str
    family_name: Optional[str] = None
    phone_number: PhoneNumber

    @field_validator("email")
    @classmethod
    def lower_case_email(cls, value: str) -> str:
        return value.lower()


class UserUpdate(schemas.BaseUserUpdate):
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    phone_number: Optional[PhoneNumber] = None

    @field_validator("email")
    @classmethod
    def lower_case_email(cls, value: str) -> str:
        return value.lower()


class UserView(schemas.BaseUser[PydanticObjectId]):
    """
    Fields when returning a user. Don't send the password.
    """

    id: PydanticObjectId
    email: EmailStr
    given_name: str
    family_name: Optional[str] = None
    phone_number: Optional[types.PhoneNumber]


class AbridgedUser(BaseModel):
    """
    Just the minimum fields when returning a user
    """

    id: PydanticObjectId
    email: EmailStr


class UserRoles(BaseModel):
    application_administrator: bool = False
