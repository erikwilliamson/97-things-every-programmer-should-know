# Standard Library Imports
from enum import IntEnum, StrEnum


class Currency(StrEnum):
    CAD = "cad"
    USD = "usd"


class Country(StrEnum):
    CA = "CA"


class EntityType(StrEnum):
    COMPANY = "company"
    LOCATION = "location"
    ROOM = "room"
    BOOKING = "booking"
    COLLECTIVE = "collective"
    INVOICE = "invoice"


class HealthCheckStatus(StrEnum):
    OK = "ok"
    NOT_OK = "not ok"


class SocialMediaPlatform(StrEnum):
    FACEBOOK = "Facebook"
    TWITTER = "Twitter"
    INSTAGRAM = "Instagram"
    MYSPACE = "MySpace"
    FRIENDSTER = "Friendster"
    AOL = "AOL"


class RoomUses(StrEnum):
    """
    Tags for what a room can be used for
    """

    LIVE = "Live"
    LIVE_STREAM = "Live Stream"
    LARGE_GROUP = "Large Group"
    PODCASTING = "Podcasting"
    REHEARSAL = "Rehearsal"
    RECORDING = "Recording"
    BROADCASTING = "Broadcasting"
    POST_PRODUCTION = "Post-Production"


class DayOfWeek(IntEnum):
    """
    Days of the Week - ISO Standard - is this really necessary?
    https://docs.python.org/3/library/datetime.html#datetime.date.isoweekday
    """

    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6
    SUNDAY = 7


class UnitOfMeasure(StrEnum):
    """
    Units of measure
    """

    METRIC = "metric"
    IMPERIAL = "imperial"


class BookingInterval(StrEnum):
    HOURLY = "hourly"
    DAILY = "daily"


class BookingTier(StrEnum):
    SINGLE = "single"
    GROUP = "group"
    VIP = "vip"


class Role(StrEnum):
    """
    User Roles
    """

    ANY = "any"
    NONE = "none"
    SELF = "self"
    APPLICATION_ADMINISTRATOR = "application_administrator"
    COMPANY_ADMINISTRATOR = "company_administrator"
    LOCATION_ADMINISTRATOR = "location_administrator"
    BOOKING_CREATOR = "booking_creator"
    BOOKING_OWNER = "booking_owner"
    BOOKING_PARTICIPANT = "booking_participant"
    MUSICIAN = "musician"


class StudioType(StrEnum):
    """
    Types of Studios
    """

    COMMERCIAL = "commercial"
    RESIDENTIAL = "residential"


class PaymentStatus(StrEnum):
    """
    Payment Statuses
    """

    PENDING = "pending"
    PAID = "paid"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"
