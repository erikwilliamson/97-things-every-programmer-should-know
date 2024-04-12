# Standard Library Imports
import json
import logging
import pathlib
import random

# 3rd-Party Imports
from fastapi import APIRouter, BackgroundTasks, Depends, Response, status
from fastapi.exceptions import HTTPException

# Application-Local Imports
from ninety_seven_things.core.config import settings
from ninety_seven_things.modules.author import schemas as author_schemas
from ninety_seven_things.modules.author import service as author_service
from ninety_seven_things.modules.article import schemas as article_schemas
from ninety_seven_things.modules.article import service as article_service
from ninety_seven_things.modules.user import dependencies as user_dependencies
from ninety_seven_things.modules.user import exceptions as user_exceptions
from ninety_seven_things.modules.user import models as user_models
from ninety_seven_things.modules.user import schemas as user_schemas
from ninety_seven_things.modules.user import service as user_service

# Local Folder Imports
from .role import allow_reseed_db, allow_wipe_db
from .schemas import LoadedDataReport
from .service import clear_db, load_seed_data, insert_erik

router = APIRouter()
logger = logging.getLogger(settings.LOG_NAME)


@router.post(
    path="/erik",
    status_code=status.HTTP_201_CREATED,
    summary="Creates Erik",
    responses={
        status.HTTP_201_CREATED: {
            "content": {"application/json": {"schema": {"title": "Fooooo"}}},
        }
    },
)
async def erik() -> Response:
    await insert_erik()
    return Response(status_code=status.HTTP_201_CREATED)


@router.post(
    path="/load_seed_data",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(allow_reseed_db)],
    summary="Loads Seed Data",
    responses={
        status.HTTP_201_CREATED: {
            "content": {"application/json": {"schema": {"title": "FOOOOOOOO"}}},
        }
    },
)
async def load_seed_data(
    user_roles: user_dependencies.UserRoleDependency,
    background_tasks: BackgroundTasks,
    bookings_per_room_min: int = 10,
    bookings_per_room_max: int = 20,
    wipe: bool = True,
    create_bookings: bool = True,
    filename: str = "examples/minimal.json",
) -> LoadedDataReport:
    seed_data = pathlib.Path(f"/app/data/{filename}")

    if wipe:
        logger.info("Wiping DB")
        await clear_db()

    try:
        with open(seed_data, "r") as f:
            seed_data = json.loads(f.read())
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"File not found: {seed_data}") from exc

    created_users = []
    created_authors = []
    created_articles = []

    if "users" in seed_data:
        for user in seed_data["users"]:
            logger.info(f"Creating User: {user['email']}")
            try:
                created_user = await user_service.create_user(user_in=user_schemas.UserCreate(**user))
            except user_exceptions.UserExistsException:
                logger.info(f"User already exists: {user['email']}")
            else:
                logger.info(f"Created User: {created_user.email}")
                created_users.append(created_user.id)

    if "collectives" in seed_data:
        for collective_data in seed_data["collectives"]:
            logger.info(f"Creating Collective: {collective_data['name']}")
            created_members = []
            for member in collective_data["members"]:
                logger.info(f"Creating Member: {member['email']}")
                try:
                    user = await user_service.create_user(user_in=user_schemas.UserCreate(**member))
                except user_exceptions.UserExistsException:
                    logger.info(f"Member already exists: {member['email']}")
                else:
                    logger.info(f"Created Member: {user.email}")
                    created_members.append(user.id)

            collective_data["members"] = created_members

            logger.info(f"collective['members']: {collective_data['members']}")

            collective = await collective_service.create(
                collective_in=collective_schemas.CollectiveCreate(**collective_data)
            )

            created_collectives.append(collective)

    created_bookings_count = 0

    if "companies" in seed_data:
        for company in seed_data["companies"]:
            logger.info(f"Creating Company: {company['name']}")

            try:
                created_company = await company_service.create(
                    company_in=company_schemas.CompanyCreate(**company),
                    background_tasks=background_tasks,
                )
            except company_exceptions.CompanyException as exc:
                logger.error(f"Error creating company: {exc}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error creating company: {exc}",
                )

            logger.info(f"Created Company: {created_company.name}")
            created_companies.append(created_company.name)

            for location in company["locations"]:
                logger.info(f"Creating Location: {location['name']}")

                try:
                    created_location = await location_service.create(
                        company_id=created_company.id,
                        location_in=location_schemas.LocationCreate(**location),
                        background_tasks=background_tasks,
                    )
                except location_exceptions.LocationException as exc:
                    logger.error(f"Error creating location: {exc}")
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=f"Error creating location: {exc}",
                    )

                logger.info(f"Created Location: {created_location.name}")
                created_locations.append(f"{created_company.name} / {created_location.name}")

                await standard_business_hours_flows.set_all_standard_business_hours(
                    location_id=created_location.id,
                    business_hours_in=standard_business_hours_schemas.BatchBusinessHoursCreate(
                        **location["business_hours"]
                    ),
                )

                for room in location["rooms"]:
                    logger.info(f"Creating Room: {room['name']}")
                    created_room = await room_service.create(
                        location_id=created_location.id, room_in=room_schemas.RoomCreate(**room)
                    )

                    logger.info(f"Created Room: {created_room.name}")
                    created_rooms.append(f"{created_company.name} / {created_location.name} / {created_room.name}")

                    if not create_bookings:
                        continue

                    if created_members:
                        for _ in range(random.randint(bookings_per_room_min - 1, bookings_per_room_max)):
                            try:
                                booking_in = await booking_flows.generate_booking(
                                    room_id=created_room.id,
                                    booked_for=random.choice(created_members),
                                )
                            except booking_exceptions.BookingException:
                                logger.warning(f"Failed to create booking for room {created_room.id}")
                                continue
                            else:
                                logger.info(f"Creating Booking for room {created_room.id}")

                            created_by = await user_service.get_one_by_id(user_id=random.choice(created_users))
                            try:
                                await booking_service.create(
                                    user_roles=user_roles,
                                    booking_in=booking_in,
                                    created_by=created_by.id,
                                    room_id=created_room.id,
                                )
                            except booking_exceptions.BookingException as exc:
                                logger.warning(f"Failed to create booking for room {created_room.id}: {exc.message}")
                            else:
                                created_bookings_count += 1

    logger.info(f"Created {created_bookings_count} bookings")

    return LoadedDataReport(
        companies=created_companies,
        locations=created_locations,
        rooms=created_rooms,
        collectives=[c.name for c in created_collectives],
        users=created_users,
        members=created_members,
        bookings_count=created_bookings_count,
    )


@router.delete(
    path="/wipe",
    response_class=Response,
    dependencies=[Depends(allow_wipe_db)],
    summary="Deletes everything",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def clear_db():
    """
    delete (pretty much) everything
    """

    models = [
        room_models.Room,
        location_models.Location,
        company_models.Company,
        booking_models.Booking,
        company_models.VIPList,
        collective_models.Collective,
        user_models.User,
    ]

    for model in models:
        logger.warning(f"Deleting all {model.__name__} documents")
        await model.delete_all()
