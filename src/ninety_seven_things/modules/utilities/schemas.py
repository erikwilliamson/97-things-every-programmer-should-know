# Standard Library Imports
from typing import List

# 3rd-Party Imports
from beanie import PydanticObjectId
from pydantic import BaseModel


class LoadedDataReport(BaseModel):
    authors: List[str]
    articles: List[PydanticObjectId]
