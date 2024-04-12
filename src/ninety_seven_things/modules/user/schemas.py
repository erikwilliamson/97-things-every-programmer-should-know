# Future Imports
from __future__ import annotations

# Standard Library Imports
import logging
from typing import Dict, List, Optional

# 3rd-Party Imports
from beanie import PydanticObjectId
from fastapi_users import schemas
from pydantic import BaseModel, EmailStr, field_validator

# Application-Local Imports
from wj.core.config import settings
from wj.lib import types
from wj.lib.types.phone_number import PhoneNumber

# from wj.modules.address import schemas as address_schemas

logger = logging.getLogger(settings.LOG_NAME)


class AnonymousUserCreate(BaseModel):
    given_name: str
    family_name: Optional[str] = None
    phone_number: PhoneNumber
    email: EmailStr


class UserCreate(schemas.BaseUserCreate):
    given_name: str
    family_name: Optional[str] = None
    phone_number: PhoneNumber
    is_anonymous: bool = False
    # address: address_schemas.Address

    @field_validator("email")
    @classmethod
    def lower_case_email(cls, value: str) -> str:
        return value.lower()


class UserUpdate(schemas.BaseUserUpdate):
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    phone_number: Optional[PhoneNumber] = None
    # address: address_schemas.Address

    @field_validator("email")
    @classmethod
    def lower_case_email(cls, value: str) -> str:
        return value.lower()


class UserRoleContext(BaseModel):
    company: Optional[Dict[PydanticObjectId, str]] = None
    location: Optional[Dict[PydanticObjectId, str]] = None
    collective: Optional[Dict[PydanticObjectId, str]] = None
    booking: Optional[Dict[PydanticObjectId, str]] = None


class UserRoles(BaseModel):
    user_id: PydanticObjectId = None
    anonymous_user: bool = False
    application_administrator: bool = False
    company_administrator: List[PydanticObjectId] = []
    location_administrator: List[PydanticObjectId] = []
    collective_member: List[PydanticObjectId] = []
    bookings: List[PydanticObjectId] = []


class UserView(schemas.BaseUser[PydanticObjectId]):
    """
    Fields when returning a user. Don't send the password.
    """

    id: PydanticObjectId
    email: EmailStr
    given_name: str
    family_name: Optional[str] = None
    phone_number: Optional[types.PhoneNumber]
    is_anonymous: bool
    registered_account: Optional[UserView] = None
    # unregistered_accounts: Optional[List["UserView"]] = None


class AbridgedUser(BaseModel):
    """
    Just the minimum fields when returning a user
    """

    id: PydanticObjectId
    email: EmailStr


class ImpersonationResponse(BaseModel):
    access_token: str
    token_type: str
    impersonator: PydanticObjectId
