from typing import Annotated

from fastui import FastUI, AnyComponent, components as c
from fastui.components.display import DisplayMode, DisplayLookup
from fastui.events import GoToEvent, BackEvent
from pydantic import BaseModel, Field

from fastapi import APIRouter
import logging
from ninety_seven_things.core.config import settings
from ninety_seven_things.modules.event import service as event_service
from beanie import PydanticObjectId
from icecream import ic
from ninety_seven_things.modules.event import schemas as event_schemas
from . import application_page
from fastui.forms import fastui_form, SelectSearchResponse

router = APIRouter()
logger = logging.getLogger(settings.LOG_NAME)


class EventForm(BaseModel):
    name: str | None = Field(
        None, description='This field is not required, it must start with a capital letter if provided'
    )

@router.post(path='/event', response_model=FastUI, response_model_exclude_none=True)
async def create_event_form(form: Annotated[event_schemas.EventCreate, fastui_form(event_schemas.EventCreate)]):
    await event_service.create(event_in=form)
    return [c.FireEvent(event=GoToEvent(url='/event'))]


@router.get(path='/event/create', response_model=FastUI, response_model_exclude_none=True)
def form_content():
    return application_page(
        c.Paragraph(text="Let's create an event!"),
        c.ModelForm(model=event_schemas.EventCreateForm, display_mode='page', submit_url='/ui/event'),
        title="Create Event"
    )


@router.get(path="/event/search", response_model=SelectSearchResponse)
async def search_view(q: str) -> SelectSearchResponse:
    events = await event_service.search_by_name(partial_name=q)
    event_options = [{'label': event.name, 'value': str(event.id)} for event in events]

    options = [
        {'label': "Event", 'options': event_options}
    ]

    return SelectSearchResponse(options=options)


@router.get(path="/event", response_model=FastUI, response_model_exclude_none=True)
async def event_table() -> list[AnyComponent]:
    events = await event_service.get_many(fetch_links=True)

    return application_page(
        # c.Heading(text='Events', level=2),
        c.Table(
            data=events,
            columns=[
                DisplayLookup(field='name', on_click=GoToEvent(url='/event/{_id}')),
                DisplayLookup(field='timezone', mode=DisplayMode.plain),
                DisplayLookup(field='organization', mode=DisplayMode.plain),
                DisplayLookup(field='track_count', mode=DisplayMode.plain),
            ],
            data_model=event_service.Event
        ),
        c.Link(
            components=[c.Text(text='Create New Event')],
            on_click=GoToEvent(url="/event/create")
        ),
        title="Events"
    )


@router.get(path="/event/{event_id}", response_model=FastUI, response_model_exclude_none=True, include_in_schema=False)
async def event_detail(event_id: PydanticObjectId) -> list[AnyComponent]:
    """
    event page, the frontend will fetch this when the user visits `/event/{id}/`.
    """
    event = await event_service.get_by_id(event_id, fetch_links=True)

    return application_page(
        # c.Heading(text=event.name, level=2),
        c.Link(components=[c.Text(text='Back')], on_click=BackEvent()),
        c.Details(
            data=event,
            fields=[
                DisplayLookup(field='name'),
                DisplayLookup(field='timezone'),
                DisplayLookup(field='organization'),
                DisplayLookup(field='tracks'),
            ]
        ),
        title="Event Detail"
    )
