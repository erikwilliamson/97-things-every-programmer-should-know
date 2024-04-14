# Standard Library Imports
import datetime

# 3rd-Party Imports
from pydantic import Field, field_serializer

# Application-Local Imports
from ninety_seven_things.lib import constants, helpers


class Timestamped:
    created_at: datetime.datetime = Field(default_factory=helpers.utcnow)
    updated_at: datetime.datetime = Field(default_factory=helpers.utcnow)

    @field_serializer("created_at", "updated_at")
    def serialize_created_at(self, created_at: datetime.datetime) -> str:
        return created_at.strftime(constants.HUMAN_READABLE_DATETIME_FORMAT)
