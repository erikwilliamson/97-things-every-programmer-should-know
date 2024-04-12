# Standard Library Imports
import logging
import pathlib
import sys
from contextlib import asynccontextmanager
from typing import Any, Dict

# 3rd-Party Imports
from beanie import init_beanie
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.responses import FileResponse, RedirectResponse
from motor.motor_asyncio import AsyncIOMotorClient
from starlette.middleware.cors import CORSMiddleware

# Application-Local Imports
from ninety_seven_things import __version__
from ninety_seven_things.core import config
from ninety_seven_things.core import logging as wj_logging
from ninety_seven_things.lib import constants, exceptions, helpers
from ninety_seven_things.modules.article import models as article_models
from ninety_seven_things.modules.author import models as author_models

try:
    wj_logging.init_logging()
except exceptions.ConfigurationException:
    sys.exit(constants.E_CONFIG)

logger = logging.getLogger(config.settings.LOG_NAME)
logger.info(f"Welcome to the {config.settings.PROJECT_NAME}")


def custom_openapi() -> Dict[str, Any]:
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=config.settings.PROJECT_NAME,
        version=__version__,
        routes=app.routes,
    )

    app.openapi_schema = helpers.change_union_serialization(openapi_schema)
    return app.openapi_schema


@asynccontextmanager
async def lifespan(application: FastAPI):  # type: ignore
    """Initialize application services."""
    logger.info(f"Connecting to mongo at {config.settings.MONGO_URL}")

    client = AsyncIOMotorClient(config.settings.MONGO_URL)
    application.db = client[config.settings.MONGO_DBNAME]

    logger.info("Starting ODM initialization")

    await init_beanie(
        database=application.db,
        document_models=[
            author_models.Author,
            article_models.Article,
        ],
    )

    logger.info("ODM initialization complete")

    yield

    logger.info("Shutdown complete")


if config.settings.ENVIRONMENT not in config.SHOW_DOCS_ENVIRONMENTS:
    openapi_url = None
else:
    openapi_url = "/api/v1/openapi.json"

logger.info("Creating application instance")

app = FastAPI(
    title=config.settings.PROJECT_NAME,
    description=config.settings.PROJECT_NAME,
    openapi_url=openapi_url,
    lifespan=lifespan,
)

logger.info("Tweaking OpenAPI schema")
app.openapi = custom_openapi

# Set all CORS enabled origins
if config.settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in config.settings.BACKEND_CORS_ORIGINS],
        allow_origin_regex=config.settings.BACKEND_CORS_ORIGINS_REGEX,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

logger.info("Simplifying operation IDs")
helpers.simplify_operation_ids(app)


@app.get(path="/", include_in_schema=False)
async def redirect() -> RedirectResponse:
    response = RedirectResponse(url="/docs")
    return response


@app.get(path="/favicon.ico", include_in_schema=False)
async def get_favicon() -> FileResponse:
    favicon_path = pathlib.Path(__file__).parent / "static" / "favicon.ico"
    return FileResponse(favicon_path)


#
# @app.exception_handler(ManagementAPIException)
# async def management_api_exception_handler(request: Request, exc: ManagementAPIException):
#     return ManagementAPIExceptionResponse(detail=exc.errors(), status_code=exc.status_code)
#
