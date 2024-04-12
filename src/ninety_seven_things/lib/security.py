# Standard Library Imports
import logging
from typing import Optional

# 3rd-Party Imports
import redis.asyncio
from beanie import PydanticObjectId
from fastapi import Depends, Request, Response
from fastapi_users import BaseUserManager, FastAPIUsers
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, RedisStrategy
from fastapi_users_db_beanie import BeanieUserDatabase, ObjectIDIDMixin
from icecream import ic

# Application-Local Imports
from ninety_seven_things.core.config import settings
from ninety_seven_things.lib.exceptions import AuthenticationException, DoesNotExistException
from ninety_seven_things.lib.helpers import get_base_url
from ninety_seven_things.lib.passwords import verify_password
from ninety_seven_things.modules.mail import service as mail_flows
from ninety_seven_things.modules.user import models as user_models
from ninety_seven_things.modules.user import service as user_service

logger = logging.getLogger(settings.LOG_NAME)

bearer_transport = BearerTransport(tokenUrl="api/v1/auth/login")
# redis = redis.asyncio.from_url(str(settings.REDIS_URL), decode_responses=True)
redis = redis.asyncio.from_url(settings.REDIS_URL, decode_responses=True)


def get_redis_strategy() -> RedisStrategy:
    return RedisStrategy(redis, lifetime_seconds=settings.AUTH_TOKEN_LIFETIME)


class UserManager(ObjectIDIDMixin, BaseUserManager[user_models.User, PydanticObjectId]):
    reset_password_token_secret = settings.SECRET_KEY
    verification_token_secret = settings.SECRET_KEY

    async def on_after_register(self, user: user_models.User, request: Optional[Request] = None) -> None:
        logger.info(f"User {user.id} has registered.")

        confirmation_link = f"{get_base_url()}/user/{user.id}/confirmation"

        logger.info(f"sending user confirmation email to {user.email} -- {user.given_name} {user.family_name}")

        mail_flows.send_new_account_confirmation_mail(
            mail_to=user.email,
            given_name=user.given_name,
            family_name=user.family_name,
            confirmation_link=confirmation_link,
        )

    async def on_after_login(
        self,
        user: user_models.User,
        request: Optional[Request] = None,
        response: Optional[Response] = None,
    ) -> None:
        logger.info(f"User {user.id} has logged in")
        ic()

    async def on_after_update(self, user: user_models.User, token: str, request: Optional[Request] = None) -> None:
        logger.info(f"User {user.id} has been updated")

    async def on_after_verify(self, user: user_models.User, request: Optional[Request] = None) -> None:
        logger.info(f"User {user.id} has been updated")

    async def on_before_delete(self, user: user_models.User, request: Optional[Request] = None) -> None:
        logger.info(f"User {user.id} has been updated")

    async def on_after_delete(self, user: user_models.User, request: Optional[Request] = None) -> None:
        logger.info(f"User {user.id} has been updated")

    async def on_after_forgot_password(
        self, user: user_models.User, token: str, request: Optional[Request] = None
    ) -> None:
        logger.info(f"User {user.id} has forgotten their password. Reset token: {token}")
        logger.warning(f"Request: {request}")
        logger.warning(f"Request: {dir(request)}")
        logger.warning(f"Request.client: {request.client}")
        logger.warning(f"Request.headers: {request.headers}")
        logger.warning(f"Request.client (dir): {dir(request.client)}")

        base_url = request.headers.get("origin", get_base_url())

        mail_flows.send_forgot_password_mail(
            mail_to=user.email,
            given_name=user.given_name,
            family_name=user.family_name,
            token=token,
            base_url=base_url,
        )

    async def on_after_reset_password(self, user: user_models.User, request: Optional[Request] = None) -> None:
        logger.info(f"User {user.id} has reset their password.")

        mail_flows.send_reset_password_mail(
            mail_to=user.email,
            given_name=user.given_name,
            family_name=user.family_name,
            base_url=request.headers.get("origin", get_base_url()),
        )

    async def on_after_request_verify(
        self, user: user_models.User, token: str, request: Optional[Request] = None
    ) -> None:
        logger.info(f"Verification requested for user {user.id}. Verification token: {token}")


async def get_user_manager(user_db: BeanieUserDatabase = Depends(user_models.get_user_db)) -> UserManager:
    yield UserManager(user_db)


async def authenticate_user(username: str, password: str) -> user_models.User:
    try:
        user = await user_service.get_one_by_email(email=username)
    except DoesNotExistException as exc:
        raise AuthenticationException from exc

    if not verify_password(password, user.hashed_password):
        raise AuthenticationException

    return user


auth_backend = AuthenticationBackend(
    name="redis",
    transport=bearer_transport,
    get_strategy=get_redis_strategy,
)

fastapi_users = FastAPIUsers[user_models.User, PydanticObjectId](get_user_manager, [auth_backend])

current_active_user = fastapi_users.current_user(active=True, optional=True)
