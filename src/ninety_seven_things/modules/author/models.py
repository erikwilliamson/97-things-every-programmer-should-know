# Standard Library Imports
import logging

# 3rd-Party Imports
from beanie import Document
from pydantic import computed_field

# Application-Local Imports
from ninety_seven_things.core.config import settings


logger = logging.getLogger(settings.LOG_NAME)


class Author(Document):
    given_name: str
    family_name: str
    url: str

    @computed_field
    @property
    def full_name(self) -> str:
        if self.family_name:
            return f"{self.given_name} {self.family_name}"

        return self.given_name
