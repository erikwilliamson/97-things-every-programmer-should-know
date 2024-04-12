# Standard Library Imports
import datetime
from pathlib import Path
from typing import List

# 3rd-Party Imports
from pydantic import AnyHttpUrl, EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict

path = Path(__file__)
base_dir = path.parent.parent.parent.parent

SHOW_DOCS_ENVIRONMENTS = ("development", "qa", "testing")


class Settings(BaseSettings):
    """
    Type declarations & default values for settings
    """

    model_config = SettingsConfigDict(
        # `.env.prod` takes priority over `.env`
        # env_file=(".env", ".env.testing")
        env_file=(".env.testing", ".env")
        # env_file=".env"
    )

    # General
    PROJECT_NAME: str = "97 Things Every Programmer Should Know"
    API_PREFIX: str = "/api/v1"
    API_BOOT_TIME: datetime.datetime = datetime.datetime.now(datetime.UTC)
    API_PORT: int
    API_HOST: str = "0.0.0.0"
    ENVIRONMENT: str

    # OpenAPI
    OPENAPI_URL: str = f"{API_PREFIX}/openapi.json"

    # Authentication / Authorization
    AUTH_TOKEN_LIFETIME: int
    SECRET_KEY: str
    ALGORITHM: str
    IMPERSONATION_TOKEN_LIFETIME: int
    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int

    # Data Store
    DATA_DIR: str

    # Data Source
    SOURCE_REPO_URL: AnyHttpUrl

    # Alerting
    ALERT_EMAIL_RECIPIENT: EmailStr

    # Units of Measure
    UNIT_OF_MEASURE: str = "metric"  # "imperial"

    # Email
    MAIL_TEMPLATE_DIR: str
    MAIL_FROM_NAME: str
    MAIL_FROM_ADDRESS: EmailStr
    MAIL_ENABLED: bool
    SENDGRID_API_KEY: str

    # SMS
    TWILIO_API_SID: str
    TWILIO_API_AUTH_TOKEN: str
    TWILIO_SENDER: str

    # Logging
    LOG_NAME: str = "97_things"
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "/tmp/97_things.log"

    # Mongo Database
    MONGO_URL: str
    MONGO_DBNAME: str
    MONGO_PORT: int

    # Redis DB
    REDIS_URL: str
    REDIS_PORT: int

    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    BACKEND_CORS_ORIGINS_REGEX: str = ""


env_file = f"{base_dir}/.env"
settings = Settings()
