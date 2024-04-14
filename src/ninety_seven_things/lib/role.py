# Standard Library Imports
import logging
from enum import Enum
from typing import List

# 3rd-Party Imports
from fastapi import Depends, Request
from fastapi.exceptions import HTTPException
from icecream import ic

# Application-Local Imports
from ninety_seven_things.core.config import settings
from ninety_seven_things.lib import enums
from ninety_seven_things.lib.security import current_active_user
from ninety_seven_things.modules.user import dependencies as user_dependencies
from ninety_seven_things.modules.user import models as user_models

logger = logging.getLogger(settings.LOG_NAME)


class RoleChecker:
    def __init__(
        self,
        allowed_roles: List[Enum],
    ):
        self.allowed_roles = allowed_roles

    async def __call__(
        self,
        request: Request,
        user_roles: user_dependencies.UserRoleDependency,
        user: user_models.User = Depends(current_active_user),
    ) -> None:
        if enums.Role.ANY in self.allowed_roles:
            ic()
            logger.debug("allowing ANY role through")
            return

        if enums.Role.NONE in self.allowed_roles:
            ic()
            logger.debug("disallowing NONE role through")
            raise HTTPException(status_code=403, detail="Operation not permitted")

        if enums.Role.APPLICATION_ADMINISTRATOR in self.allowed_roles:
            ic()
            if user and user.is_superuser:
                ic()
                logger.debug("allowing superuser through")
                return

        message = f"{user.email} is not a superuser"
        logger.debug(message)
        raise HTTPException(status_code=403, detail="Operation not permitted")
