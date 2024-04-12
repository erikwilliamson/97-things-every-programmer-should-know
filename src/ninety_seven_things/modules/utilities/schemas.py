# Standard Library Imports
from typing import List

# 3rd-Party Imports
from pydantic import BaseModel


class LoadedDataReport(BaseModel):
    authors: List[str]
    articles: List[str]
