# Standard Library Imports
import logging

# 3rd-Party Imports
from beanie import PydanticObjectId
from fastapi import APIRouter
from fastui import AnyComponent, FastUI
from fastui import components as c
from fastui.components.display import DisplayLookup, DisplayMode
from fastui.events import BackEvent, GoToEvent
from icecream import ic
from pydantic import BaseModel, Field

# Application-Local Imports
from ninety_seven_things.core.config import settings
from ninety_seven_things.modules.article import models as article_models
from ninety_seven_things.modules.article import service as article_service

# Local Folder Imports
from . import admin_page

router = APIRouter()
logger = logging.getLogger(settings.LOG_NAME)


@router.get(path="/article", response_model=FastUI, response_model_exclude_none=True)
async def article_table() -> list[AnyComponent]:
    articles = await article_service.get_all(fetch_links=True)

    return admin_page(
        c.Table(
            data=articles,
            columns=[
                DisplayLookup(field="index", mode=DisplayMode.plain),
                DisplayLookup(field="title", on_click=GoToEvent(url="/admin/article/{_id}")),
                DisplayLookup(field="language", mode=DisplayMode.plain),
            ],
            data_model=article_models.Article,
        ),
        title="Articles",
    )


@router.get(
    path="/article/{article_id}", response_model=FastUI, response_model_exclude_none=True, include_in_schema=False
)
async def article_detail(article_id: PydanticObjectId) -> list[AnyComponent]:
    """
    article page, the frontend will fetch this when the user visits `/admin/article/{id}/`.
    """
    article = await article_service.get_by_id(article_id, fetch_links=True)

    ic(article)
    return admin_page(
        # c.Heading(text=article.name, level=2),
        c.Link(components=[c.Text(text="Back")], on_click=BackEvent()),
        c.Details(
            data=article,
            fields=[
                DisplayLookup(field="title"),
                DisplayLookup(field="index"),
                DisplayLookup(field="contents", mode=DisplayMode.markdown),
            ],
        ),
        title="Article Detail",
    )
