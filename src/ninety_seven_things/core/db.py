# Standard Library Imports
import logging

# 3rd-Party Imports
import motor.motor_asyncio

# Application-Local Imports
from ninety_seven_things.core.config import settings

logger = logging.getLogger(settings.LOG_NAME)


def get_mongo_uri(hosts: str, port: int) -> str:
    # Hosts is a comma-separated list of hosts. Explode it and insert ports.
    ported_hosts = [f"{host}:{port}" for host in hosts.split(",")]
    cluster = ",".join(ported_hosts)

    return f"mongodb://{cluster}"


logger.info("Connecting to mongo at %s", settings.MONGO_URL)
client = motor.motor_asyncio.AsyncIOMotorClient(settings.MONGO_URL, uuidRepresentation="standard")
db = client[settings.MONGODB_DBNAME]
