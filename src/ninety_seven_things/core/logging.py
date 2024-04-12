# Standard Library Imports
import logging
import sys

# Application-Local Imports
from ninety_seven_things.core.config import settings


def init_logging() -> None:
    init_stdout_logging()


def init_stdout_logging() -> None:
    root = logging.getLogger()
    root.setLevel(settings.LOG_LEVEL)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(settings.LOG_LEVEL)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    handler.setFormatter(formatter)
    root.addHandler(handler)
