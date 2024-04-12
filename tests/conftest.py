# Standard Library Imports
import asyncio
import logging
from datetime import date, timedelta
from typing import Dict, Iterator, List

# 3rd-Party Imports
import pytest
import pytest_asyncio
from asgi_lifespan import LifespanManager
from beanie import PydanticObjectId
from bson.objectid import ObjectId
from httpx import AsyncClient
from pydantic import EmailStr

# Application-Local Imports
from ninety_seven_things.core.config import settings
from ninety_seven_things.core.db import db
from ninety_seven_things.lib.types.phone_number import PhoneNumber
from ninety_seven_things.modules.company import role as company_role
from ninety_seven_things.modules.company.models import Company
from ninety_seven_things.modules.location.models import Location
from ninety_seven_things.modules.room.models import Room
from ninety_seven_things.modules.room.schemas import RoomCreate
from ninety_seven_things.modules.room.service import create as create_room
from ninety_seven_things.modules.user.models import User

logger = logging.getLogger()

settings.TESTING = True
settings.MONGODB_DBNAME = "testing"

# Application-Local Imports
from ninety_seven_things.main import app  # Noqa: E402


async def override_auth() -> None:
    logger.error("inside override_auth")
    return


@pytest.fixture(autouse=True)
def disable_authorization():
    app.dependency_overrides[current_active_user] = override_auth
    for current_role in [r for r in dir(company_role) if r.startswith("allow_")]:
        print(f"Overriding {current_role}")
        app.dependency_overrides[current_role] = override_auth


@pytest.fixture(scope="function", autouse=True)
async def client() -> Iterator[AsyncClient]:
    """Async server client that handles lifespan and teardown"""
    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url="http://test") as _client:
            try:
                yield _client
            except Exception as exc:  # pylint: disable=broad-except
                print(exc)
            finally:
                await clear_database()


@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()


async def clear_database() -> None:
    """Empties the test database"""

    for collection_name in await db.list_collection_names():
        await db.get_collection(collection_name).delete_many({})


@pytest.fixture()
async def object_id() -> PydanticObjectId:
    """generates an ObjectId"""
    return PydanticObjectId(oid=ObjectId())


@pytest_asyncio.fixture
async def user(good_user_in: Dict) -> User:
    good_user_in["hashed_password"] = "password"
    created_user = User(**good_user_in)
    await created_user.save()
    return created_user


@pytest_asyncio.fixture
async def unprivileged_user(good_user_in: Dict) -> User:
    good_user_in["hashed_password"] = "password"
    good_user_in["email"] = "unprivileged.user@example.com"
    created_user = User(**good_user_in)
    await created_user.save()
    return created_user


@pytest_asyncio.fixture
async def company_admin_user(good_user_in: Dict) -> User:
    good_user_in["hashed_password"] = "password123"
    good_user_in["email"] = "company.admin@example.com"
    created_user = User(**good_user_in)
    await created_user.save()
    return created_user


@pytest_asyncio.fixture
async def secondary_company_admin_user(good_user_in: Dict) -> User:
    good_user_in["hashed_password"] = "password123"
    good_user_in["email"] = "secondary.company.admin@example.com"
    created_user = User(**good_user_in)
    await created_user.save()
    return created_user


@pytest_asyncio.fixture
async def location_admin_user(good_user_in: Dict) -> User:
    good_user_in["hashed_password"] = "password123"
    good_user_in["email"] = "location.admin@example.com"
    created_user = User(**good_user_in)
    await created_user.save()
    return created_user


@pytest_asyncio.fixture
async def application_admin_user(good_user_in: Dict) -> User:
    good_user_in["hashed_password"] = "password123"
    good_user_in["email"] = "application.admin@example.com"
    good_user_in["is_superuser"] = True
    created_user = User(**good_user_in)
    await created_user.save()
    return created_user


@pytest_asyncio.fixture
async def company(good_company_in: Dict, company_admin_user: User) -> Company:
    good_company_in["administrators"] = [company_admin_user.id]
    good_company_in["opened_at"] = "2020-01-01 00:00:00"
    created_company = Company(**good_company_in)
    await created_company.save()
    return created_company


@pytest_asyncio.fixture
async def location_without_hours(
    company: Company, good_location_without_hours: Dict, location_admin_user: User
) -> Location:
    good_location_without_hours["administrators"] = [location_admin_user.id]
    good_location_without_hours["opened_at"] = "2020-01-01 00:00:00"
    created_location = Location(**good_location_without_hours, company=company.id)
    await created_location.save()
    return created_location


@pytest_asyncio.fixture
async def location_with_hours(company: Company, good_location_with_hours: Dict, location_admin_user: User) -> Location:
    good_location_with_hours["administrators"] = [location_admin_user.id]
    good_location_with_hours["opened_at"] = "2020-01-01 00:00:00"

    created_location = Location(**good_location_with_hours, company=company.id)

    await created_location.save()

    return created_location


@pytest.fixture
def good_room_in() -> Dict:
    return {
        "name": "Studio 5",
        "is_accessible": False,
        "description": "Hello, I'm a room description.",
        "uses": ["Podcasting", "Live"],
        "size": 400,
        "capacity": 4,
        "booking_requirements": [
            {
                "time_unit": "hourly",
                "tier": "single",
                "minimum": 4,
                "rate": 20,
            },
            {"time_unit": "daily", "tier": "single", "minimum": 1, "rate": 100},
            {"time_unit": "daily", "tier": "group", "minimum": 1, "rate": 100},
        ],
    }


@pytest_asyncio.fixture
async def room_with_hours(location_with_hours: Location, good_room_in: Dict) -> Room:
    return await create_room(room_in=RoomCreate(**good_room_in), location_id=location_with_hours.id)


@pytest_asyncio.fixture
async def room_without_hours(location_without_hours: Location, good_room_in: Dict) -> Room:
    return await create_room(room_in=RoomCreate(**good_room_in), location_id=location_without_hours.id)


@pytest.fixture
def good_hourly_booking_in(room_with_hours: Room) -> Dict:
    # Note that this will still need booked_for added to it when used

    tomorrow = date.today() + timedelta(days=1)

    return {
        "room_id": str(room_with_hours.id),
        "interval": "hourly",
        "tier": "single",
        "starts_at": f"{tomorrow.strftime('%Y-%m-%d')}T10:00",
        "ends_at": f"{tomorrow.strftime('%Y-%m-%d')}T12:00",
        "rate": 50000,
        "created_by": "erik@techsanity.ca",
        "group_size": 4,
    }


@pytest.fixture
def good_daily_booking_in(room_with_hours: Room) -> Dict:
    # Note that this will still need booked_for added to it when used

    start_date = date.today() + timedelta(days=1)
    end_date = date.today() + timedelta(days=4)

    return {
        "room_id": str(room_with_hours.id),
        "interval": "daily",
        "tier": "group",
        "starts_at": f"{start_date.strftime('%Y-%m-%d')}T10:00",
        "ends_at": f"{end_date.strftime('%Y-%m-%d')}T12:00",
        "rate": 50000,
        "created_by": "company.admin@example.com",
        "group_size": 4,
    }


@pytest.fixture
def good_location_without_hours(good_contacts_in: Dict) -> Dict:
    return {
        "name": "Casa del Bateman",
        "is_accessible": False,
        "address": {
            "country": "CA",
            "region": "ON",
            "city": "Brantford",
            "street_address": "109 Dufferin Avenue",
            "postal_code": "N3T4P9",
        },
        "administrators": ["company.admin@example.com"],
        "contacts": good_contacts_in,
        "opened_at": "2020-04-20",
    }


@pytest.fixture
def good_location_with_hours(good_location_without_hours: Dict) -> Dict:
    # closed on fridays
    good_location_without_hours.update(
        {
            "business_hours": [
                {"day_of_week": 1, "opening_time": "09:00", "closing_time": "17:00"},
                {"day_of_week": 2, "opening_time": "09:00", "closing_time": "16:00"},
                {"day_of_week": 3, "opening_time": "10:00", "closing_time": "15:00"},
                {"day_of_week": 4, "opening_time": "10:00", "closing_time": "14:00"},
                {"day_of_week": 6, "opening_time": "12:00", "closing_time": "23:00"},
                {"day_of_week": 7, "opening_time": "09:00", "closing_time": "18:00"},
            ]
        }
    )
    return good_location_without_hours


@pytest.fixture
def good_contact_given_and_family_name() -> Dict:
    return {
        "given_name": "Doug",
        "family_name": "McKenzie",
        "email": "doug@mckenzie.com",
        "phone_number": "+1 (519) 756-7644",
    }


@pytest.fixture
def good_contact_no_family_name() -> Dict:
    return {"given_name": "Agnes", "email": "agnes@dog.com", "phone_number": "+1 (416) 363-1212"}


@pytest.fixture
def good_contacts_in(good_contact_no_family_name, good_contact_given_and_family_name) -> List[Dict]:
    return [good_contact_given_and_family_name, good_contact_no_family_name]


@pytest.fixture
def good_company_in(good_contacts_in) -> Dict:
    return {
        "name": "Main Stage Rehearsal Studios",
        "url": "https://mainstagerehearsal.com",
        "type": "commercial",
        "address": {
            "country": "CA",
            "region": "ON",
            "city": "Hamilton",
            "street_address": "123 King Street",
            "postal_code": "N3T4P9",
        },
        "social_media": [
            {"platform": "AOL", "url": "https://aol.com/users/lolol"},
            {"platform": "Instagram", "url": "https://www.instagram.com/Mainstagerehearsal"},
        ],
        "administrators": ["company.admin@example.com"],
        "contacts": good_contacts_in,
        "opened_at": "2019-04-20",
        "business_number": "1111111111",
    }


"""
A base user with no permissions. When needed, just replace the email address with something else
"""


@pytest.fixture
def good_user_in():
    return {
        "email": "foo@bar.com",
        "password": "foo",
        "is_active": True,
        "is_superuser": False,
        "is_verified": False,
        "given_name": "Buddy",
        "family_name": "Rich",
        "phone_number": PhoneNumber("+1 (416) 363-1212"),
        "stripe_customer_id": "cus_OrACKq9D2gtGKM",
    }


@pytest.fixture
def good_batch_business_hours() -> Dict:
    return {
        "days": {
            1: {"opening_time": "9:00", "closing_time": "18:00"},
            2: {"opening_time": "9:00", "closing_time": "17:00"},
            3: {"opening_time": "9:00", "closing_time": "16:00"},
            4: {"opening_time": "10:00", "closing_time": "15:00"},
            6: {"opening_time": "10:00", "closing_time": "14:00"},
            7: {"opening_time": "12:00", "closing_time": "00:00"},
        }
    }
