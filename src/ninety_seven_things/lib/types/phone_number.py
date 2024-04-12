# Standard Library Imports
import logging
import random
from typing import Any, Self

# 3rd-Party Imports
import phonenumbers
from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema

# Application-Local Imports
from ninety_seven_things.core.config import settings

logger = logging.getLogger(settings.LOG_NAME)


class PhoneNumber(str):
    """
    Phone Number Pydantic type, using google's phonenumbers
    """

    @classmethod
    def generate(cls) -> Self:
        area_code = random.choice(["519", "416", "403", "226"])
        prefix = "555"
        line_number = str(random.randint(1, 9998)).zfill(4)
        while line_number in ["1111", "2222", "3333", "4444", "5555", "6666", "7777", "8888"]:
            line_number = str(random.randint(1, 9998)).zfill(4)

        return f"+1{area_code}-{prefix}-{line_number}"

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler) -> CoreSchema:
        return core_schema.no_info_after_validator_function(cls, handler(str))

    @classmethod
    def validate(cls, value: str) -> Self:
        for cruft in ["-", " ", "(", ")"]:
            value = value.replace(cruft, "")

        try:
            parsed_number = phonenumbers.parse(number=value, region="CA")
        except phonenumbers.phonenumberutil.NumberParseException as exc:
            raise ValueError("invalid phone number format") from exc

        assert phonenumbers.is_valid_number(parsed_number), f"{parsed_number} is an invalid phone number"
        assert phonenumbers.is_possible_number(parsed_number), f"{parsed_number} is an impossible phone number"

        return cls(phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164))
