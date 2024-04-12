# Standard Library Imports
from typing import List

# 3rd-Party Imports
from beanie import PydanticObjectId
from pydantic import BaseModel


class LoadedDataReport(BaseModel):
    companies: List[str]
    locations: List[str]
    rooms: List[str]
    collectives: List[str]
    users: List[PydanticObjectId]
    members: List[PydanticObjectId]
    bookings_count: int
