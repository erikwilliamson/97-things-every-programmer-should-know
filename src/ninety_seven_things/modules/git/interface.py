# Future Imports
from __future__ import annotations as _annotations

# Standard Library Imports
import logging
import pathlib
from datetime import UTC, datetime
from dataclasses import dataclass

# 3rd-Party Imports
from git import Repo

# Application-Local Imports
from ninety_seven_things.core.config import settings
from ninety_seven_things.lib import constants

# Local Folder Imports
# from .exceptions import CloneRepoException

logger = logging.getLogger(settings.LOG_NAME)


@dataclass
class Git:
    repo_url: str = settings.SOURCE_REPO_URL
    local_dir: pathlib.Path = None

    def __post_init__(self):
        if not self.local_dir:
            timestamp = datetime.now(UTC).strftime(constants.DATETIME_FORMAT)
            self.local_dir = pathlib.Path(f"{settings.DATA_DIR}/checkout/{timestamp}")

    async def clone_repo(self) -> None:
        logger.info(f"Cloning {self.repo_url} to {self.local_dir}")
        Repo.clone_from(settings.SOURCE_REPO_URL, self.local_dir)
        logger.info(f"Cloning completed successfully")
