# Future Imports
from __future__ import annotations as _annotations

# Standard Library Imports
import logging
from typing import List

# 3rd-Party Imports
from fastapi import APIRouter
from fastui import AnyComponent, FastUI
from fastui import components as c
from fastui.events import BackEvent, GoToEvent
from icecream import ic

# Application-Local Imports
from ninety_seven_things.core.config import settings

router = APIRouter()
logger = logging.getLogger(settings.LOG_NAME)


@router.get(path="/index", response_model=FastUI, response_model_exclude_none=True)
async def index(language: str) -> List[AnyComponent]:
    title = f"{settings.PROJECT_NAME}"
    components = []
    return [
        c.PageTitle(text=f"{settings.PROJECT_NAME}"),
        c.Navbar(
            title=settings.PROJECT_NAME,
            title_event=GoToEvent(url=f"/reader/{language}/index"),
            start_links=[
                c.Link(
                    components=[c.Text(text=language.upper())],
                    on_click=GoToEvent(url=f"/reader/{language}"),
                )
            ]
        ),
        c.Page(
            components=[
                *((c.Heading(text=title),) if title else ()),
                *components,
            ],
        ),
        c.Footer(extra_text=settings.PROJECT_NAME, links=[
            c.Link(components=[c.Text(text="Index")], on_click=GoToEvent(url=f"/reader/{language}/index")),
            c.Link(components=[c.Text(text="Random")], on_click=GoToEvent(url=f"/reader/{language}/article/random")),
        ]),
    ]
