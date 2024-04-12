import datetime
from pydantic import Field, field_serializer
from ninety_seven_things.lib import helpers, constants

class Timestamped:
    created_at: datetime.datetime = Field(default_factory=helpers.utcnow)
    updated_at: datetime.datetime = Field(default_factory=helpers.utcnow)

    @field_serializer('created_at', 'updated_at')
    def serialize_created_at(self, created_at: datetime.datetime) -> str:
        return created_at.strftime(constants.HUMAN_READABLE_DATETIME_FORMAT)
