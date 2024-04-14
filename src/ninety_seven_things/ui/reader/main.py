# Future Imports
from __future__ import annotations as _annotations

# Standard Library Imports
import logging
import random
from typing import List

# 3rd-Party Imports
from fastapi import APIRouter
from fastui import AnyComponent, FastUI
from fastui import components as c
from fastui.events import BackEvent, GoToEvent
from icecream import ic

# Application-Local Imports
from ninety_seven_things.core.config import settings
from ninety_seven_things.lib import constants
from ninety_seven_things.modules.article import models as article_models
from ninety_seven_things.modules.article import service as article_service

router = APIRouter()
logger = logging.getLogger(settings.LOG_NAME)


def render_reader_page(article: article_models.Article, language: str) -> list[AnyComponent]:
    return reader_page(
        c.Div(
            components=[
                c.Heading(text=f"{article.index}: {article.title}", level=1),
                c.Markdown(text=article.contents),
            ],
            class_name="border-top mt-3 pt-1",
        ),
        index=article.index,
        language=language,
    )


@router.get(path="/{language}/article/random", response_model=FastUI, response_model_exclude_none=True)
async def read_random_article(language: str) -> List[AnyComponent]:
    index = random.randint(constants.FIRST_ARTICLE_ID, constants.LAST_ARTICLE_ID)
    article = await article_service.get_by_index_and_language(index=index, language=language)
    return render_reader_page(article=article, language=language)


@router.get(path="/{language}/article/{index}", response_model=FastUI, response_model_exclude_none=True)
async def read_article(index: int, language: str) -> List[AnyComponent]:
    article = await article_service.get_by_index_and_language(index=index, language=language)
    return render_reader_page(article=article, language=language)


@router.get(path="/{language}/index", response_model=FastUI, response_model_exclude_none=True)
async def reader_index(language: str = "en") -> list[AnyComponent]:
    readme = await article_service.get_by_index_and_language(index=0, language=language)
    articles = await article_service.get_by_language(language=language)

    t = []
    for article in articles:
        if article.index == 0:  # skip including the README in the index
            continue

        t.append(f"{article.index}. [{article.title}](/reader/{language}/article/{article.index})")

    return reader_page(
        c.Div(components=[c.Markdown(text=readme.contents)]),
        c.Div(
            components=[c.Heading(text="Index", level=2), c.Markdown(text="\n".join(t))],
            class_name="border-top mt-3 pt-1",
        ),
        index=0,
        language=language,
        include_nav_links=False,
    )


def reader_page(
    *components: AnyComponent,
    title: str | None = None,
    index: int = 0,
    language: str = "en",
    include_nav_links: bool = True,
) -> list[AnyComponent]:
    if not include_nav_links:
        nav_links = []
    else:
        nav_links = [
            c.Link(components=[c.Text(text="Index")], on_click=GoToEvent(url=f"/reader/{language}/index")),
            c.Link(components=[c.Text(text="Random")], on_click=GoToEvent(url=f"/reader/{language}/article/random")),
        ]

        if index > constants.FIRST_ARTICLE_ID:
            nav_links.insert(
                0,
                c.Link(
                    components=[c.Text(text="Previous")],
                    on_click=GoToEvent(url=f"/reader/{language}/article/{index - 1}"),
                ),
            )

        if index < constants.LAST_ARTICLE_ID:
            nav_links.append(
                c.Link(
                    components=[c.Text(text="Next")],
                    on_click=GoToEvent(url=f"/reader/{language}/article/{index + 1}"),
                )
            )

    start_links = []

    if index == constants.INDEX_ID:
        for language in constants.SUPPORTED_LANGUAGES:
            start_links.append(
                c.Link(components=[c.Text(text=language.upper())], on_click=GoToEvent(url=f"/reader/{language}/index"))
            )
    else:
        for language in constants.SUPPORTED_LANGUAGES:
            start_links.append(
                c.Link(
                    components=[c.Text(text=language.upper())],
                    on_click=GoToEvent(url=f"/reader/{language}/article/{index}"),
                )
            )

    return [
        c.PageTitle(text=f"{settings.PROJECT_NAME} — {title}" if title else settings.PROJECT_NAME),
        c.Navbar(
            title=settings.PROJECT_NAME, title_event=GoToEvent(url=f"/reader/{language}/index"), start_links=start_links
        ),
        c.Page(
            components=[
                *((c.Heading(text=title),) if title else ()),
                *components,
            ],
        ),
        c.Footer(extra_text=settings.PROJECT_NAME, links=nav_links),
    ]
