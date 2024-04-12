# Standard Library Imports
import logging

from icecream import ic
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastui import prebuilt_html

# Application-Local Imports
from ninety_seven_things.app import app
from ninety_seven_things.core.config import settings
from ninety_seven_things.lib.security import auth_backend, fastapi_users
from ninety_seven_things.modules.article.views import router as article_ui_router
from ninety_seven_things.modules.article.views import router as article_router
from ninety_seven_things.modules.author.views import router as author_ui_router
from ninety_seven_things.modules.author.views import router as author_router
from ninety_seven_things.modules.utilities.views import router as utilities_router

logger = logging.getLogger(settings.LOG_NAME)
logger.info("Loading routers")

# User Interface Routers
app.include_router(article_ui_router, prefix="/ui", include_in_schema=False)
app.include_router(author_ui_router, prefix="/ui", include_in_schema=False)
app.include_router(organization_ui_router, prefix="/ui", include_in_schema=False)
app.include_router(event_ui_router, prefix="/ui", include_in_schema=False)
app.include_router(speaker_ui_router, prefix="/ui", include_in_schema=False)
app.include_router(speaker_ui_router, prefix="/ui", include_in_schema=False)
app.include_router(sponsor_ui_router, prefix="/ui", include_in_schema=False)
app.include_router(sponsor_ui_router, prefix="/ui", include_in_schema=False)
app.include_router(track_ui_router, prefix="/ui", include_in_schema=False)
app.include_router(agent_ui_router, prefix="/ui", include_in_schema=False)

# API Routers
app.include_router(utilities_router, tags=["Utilities"], prefix="/api/v1")
app.include_router(user_router, tags=["User"], prefix="/api/v1")
app.include_router(organization_router, tags=["Organization"], prefix="/api")
app.include_router(status_router, tags=["Status"], prefix="/api/v1")
app.include_router(
    fastapi_users.get_auth_router(backend=auth_backend, requires_verification=True),
    prefix="/api/v1/auth",
    tags=["Authentication"],
)
app.include_router(
    fastapi_users.get_register_router(user_schemas.UserView, user_schemas.UserCreate),
    prefix="/api/v1/auth",
    tags=["Authentication"],
)
app.include_router(fastapi_users.get_reset_password_router(), prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(
    fastapi_users.get_verify_router(user_schemas.UserView),
    prefix="/api/v1/auth",
    tags=["Authentication"],
)
app.include_router(
    fastapi_users.get_users_router(user_schemas.UserView, user_schemas.UserUpdate),
    prefix="/api/v1/user",
    tags=["User"],
)

# app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/data", StaticFiles(directory=f"{settings.DATA_DIR}"), name="data")

# @app.get(path="/", include_in_schema=False)
# async def redirect() -> RedirectResponse:
#     response = RedirectResponse(url="/docs")
#     return response


# @app.get(path="/favicon.ico", include_in_schema=False)
# async def get_favicon() -> FileResponse:
#     favicon_path = pathlib.Path(__file__).parent / "static" / "favicon.ico"
#     return FileResponse(favicon_path)


#
# @app.exception_handler(ManagementAPIException)
# async def management_api_exception_handler(request: Request, exc: ManagementAPIException):
#     return ManagementAPIExceptionResponse(detail=exc.errors(), status_code=exc.status_code)
#


@app.get('/{path:path}')
async def html_landing() -> HTMLResponse:
    """Simple HTML page which serves the React app, comes last as it matches all paths."""
    return HTMLResponse(prebuilt_html(title='Speaker Seeker', api_root_url='/ui'))
