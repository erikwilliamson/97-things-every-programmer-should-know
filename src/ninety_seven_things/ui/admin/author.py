# Standard Library Imports
import logging
from typing import Annotated

# 3rd-Party Imports
from beanie import PydanticObjectId
from fastapi import APIRouter
from fastui import AnyComponent, FastUI
from fastui import components as c
from fastui.components.display import DisplayLookup, DisplayMode
from fastui.events import BackEvent, GoToEvent
from fastui.forms import SelectSearchResponse, fastui_form
from icecream import ic

# Application-Local Imports
from ninety_seven_things.core.config import settings
from ninety_seven_things.modules.author import schemas as author_schemas
from ninety_seven_things.modules.author import service as author_service

# Local Folder Imports
from . import admin_page

router = APIRouter()
logger = logging.getLogger(settings.LOG_NAME)


@router.post(path="/author", response_model=FastUI, response_model_exclude_none=True)
async def create_author_form(form: Annotated[author_schemas.AuthorCreate, fastui_form(author_schemas.AuthorCreate)]):
    # await author_service.create(**form.dict())
    await author_service.create(author_in=form)
    return [c.FireEvent(event=GoToEvent(url="/author"))]


@router.get(path="/author/create", response_model=FastUI, response_model_exclude_none=True)
def form_content():
    return admin_page(
        c.ModelForm(model=author_schemas.AuthorCreate, display_mode="page", submit_url="/ui/author"),
        title="Create Author",
    )


@router.get(path="/author", response_model=FastUI, response_model_exclude_none=True)
async def author_table() -> list[AnyComponent]:
    authors = await author_service.get_all(fetch_links=True)
    return admin_page(
        c.Table(
            data=authors,
            columns=[
                DisplayLookup(field="name", on_click=GoToEvent(url="/author/{_id}")),
                DisplayLookup(field="url", mode=DisplayMode.plain),
                DisplayLookup(field="event_count", mode=DisplayMode.plain),
                DisplayLookup(field="agent_count", mode=DisplayMode.plain),
                DisplayLookup(field="speaker_count", mode=DisplayMode.plain),
                DisplayLookup(field="sponsor_count", mode=DisplayMode.plain),
            ],
            data_model=author_service.Author,
        ),
        c.Link(components=[c.Text(text="Create New Author")], on_click=GoToEvent(url="/author/create")),
        title="Authors",
    )


@router.get(path="/author/search", response_model=SelectSearchResponse)
async def search_view(q: str) -> SelectSearchResponse:
    authors = await author_service.search_by_name(partial_name=q)
    author_options = [{"label": author.name, "value": str(author.id)} for author in authors]

    options = [{"label": "Author", "options": author_options}]
    ic(options)
    return SelectSearchResponse(options=options)


@router.get(
    path="/author/{author_id}", response_model=FastUI, response_model_exclude_none=True, include_in_schema=False
)
async def author_detail(author_id: PydanticObjectId) -> list[AnyComponent]:
    """
    author page, the frontend will fetch this when the user visits `/author/{id}/`.
    """
    author = await author_service.get_by_id(author_id, fetch_links=True)

    event_links = []
    speaker_links = []
    agent_links = []
    sponsor_links = []

    for event in author.events:
        e = await event.fetch()
        event_links.append(c.Link(components=[c.Text(text=e.name)], on_click=GoToEvent(url=f"/event/{e.id}")))

    for agent in author.agents:
        a = await agent.fetch()
        agent_links.append(c.Link(components=[c.Text(text=a.full_name)], on_click=GoToEvent(url=f"/agent/{a.id}")))

    for speaker in author.speakers:
        s = await speaker.fetch()
        speaker_links.append(c.Link(components=[c.Text(text=a.full_name)], on_click=GoToEvent(url=f"/speaker/{s.id}")))

    for sponsor in author.sponsors:
        s = await sponsor.fetch()
        sponsor_links.append(c.Link(components=[c.Text(text=a.name)], on_click=GoToEvent(url=f"/sponsor/{s.id}")))

    return admin_page(
        c.Link(components=[c.Text(text="Back")], on_click=BackEvent()),
        c.Div(
            components=[
                c.Heading(text="Details", level=2),
                c.Details(
                    data=author,
                    fields=[
                        DisplayLookup(field="name"),
                        DisplayLookup(field="url"),
                    ],
                ),
                c.Heading(text="Events", level=2),
                c.Div(components=[c.LinkList(links=event_links)], class_name="mb-4"),
                c.Heading(text="Agents", level=2),
                c.Div(components=[c.LinkList(links=agent_links)], class_name="mb-4"),
            ],
            class_name="mb-4",
        ),
    )
