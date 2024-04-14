# Standard Library Imports
import logging

# 3rd-Party Imports
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastui import prebuilt_html
from icecream import ic

# Application-Local Imports
from ninety_seven_things.app import app
from ninety_seven_things.core.config import settings
from ninety_seven_things.lib.security import auth_backend, fastapi_users
from ninety_seven_things.modules.article.views import router as article_router
from ninety_seven_things.modules.author.views import router as author_router
from ninety_seven_things.modules.user import schemas as user_schemas
from ninety_seven_things.modules.user.views import router as user_router
from ninety_seven_things.modules.utilities.views import router as utilities_router
from ninety_seven_things.ui.admin.article import router as article_admin_ui_router
from ninety_seven_things.ui.admin.author import router as author_admin_ui_router
from ninety_seven_things.ui.admin.main import router as main_admin_ui_router
from ninety_seven_things.ui.reader.main import router as main_reader_ui_router

logger = logging.getLogger(settings.LOG_NAME)
logger.info("Loading routers")

# User Interface Routers
app.include_router(article_admin_ui_router, prefix="/ui/admin", include_in_schema=False)
app.include_router(author_admin_ui_router, prefix="/ui/admin", include_in_schema=False)
app.include_router(main_admin_ui_router, prefix="/ui/admin", include_in_schema=False)

app.include_router(main_reader_ui_router, prefix="/ui/reader", include_in_schema=False)

# API Routers
app.include_router(utilities_router, tags=["Utilities"], prefix="/api/v1")
app.include_router(user_router, tags=["User"], prefix="/api/v1")
app.include_router(article_router, tags=["Article"], prefix="/api/v1")
app.include_router(author_router, tags=["Author"], prefix="/api/v1")
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


@app.get("/admin/{path:path}")
async def admin_html_landing() -> HTMLResponse:
    """Simple HTML page which serves the React app, comes last as it matches all paths."""
    return HTMLResponse(prebuilt_html(title="97 things Administration", api_root_url="/ui"))


@app.get("/reader/{path:path}")
async def reader_html_landing() -> HTMLResponse:
    """Simple HTML page which serves the React app, comes last as it matches all paths."""
    return HTMLResponse(prebuilt_html(title="97 Things Reader", api_root_url="/ui"))


routes = [{"path": route.path, "name": route.name} for route in app.routes]
ic(routes)
