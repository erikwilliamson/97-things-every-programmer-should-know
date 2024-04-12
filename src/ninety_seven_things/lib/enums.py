# Standard Library Imports
from enum import IntEnum, StrEnum


class EntityType(StrEnum):
    ARTICLE = "article"
    AUTHOR = "author"

class HealthCheckStatus(StrEnum):
    OK = "ok"
    NOT_OK = "not ok"


class Role(StrEnum):
    """
    User Roles
    """

    ANY = "any"
    NONE = "none"
    SELF = "self"
    APPLICATION_ADMINISTRATOR = "application_administrator"
