# Standard Library Imports
import logging
from datetime import UTC, datetime

# 3rd-Party Imports
from beanie import PydanticObjectId
from bson.objectid import ObjectId
from fastapi import FastAPI
from fastapi.routing import APIRoute
from pydantic import AnyHttpUrl

# Application-Local Imports
from ninety_seven_things.core.config import settings
from ninety_seven_things.lib import enums

logger = logging.getLogger(settings.LOG_NAME)


def generate_object_id() -> ObjectId:
    return PydanticObjectId(oid=ObjectId())


def get_base_url() -> AnyHttpUrl:
    if settings.API_PORT:
        port = f":{settings.API_PORT}"
    else:
        port = ""

    return AnyHttpUrl(f"http://{settings.HOST}{port}{settings.API_PREFIX}")


def simplify_operation_ids(app: FastAPI) -> None:
    """
    Simplify operation IDs so that generated clients have simpler api function names
    """
    for route in app.routes:
        if isinstance(route, APIRoute):
            route.operation_id = route.name


def utcnow() -> datetime:
    # this will allow us to use this as a Pydantic default_factory
    return datetime.now(UTC)
