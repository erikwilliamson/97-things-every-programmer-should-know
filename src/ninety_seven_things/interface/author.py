from typing import Annotated
from collections import defaultdict
from speaker_seeker.lib import helpers
from fastui import FastUI, AnyComponent, prebuilt_html, components as c
from fastui.components.display import DisplayMode, DisplayLookup, Display
from fastui.events import GoToEvent, BackEvent
from fastapi import APIRouter, Request
import logging
from speaker_seeker.core.config import settings
from speaker_seeker.modules.organization import service as organization_service
from speaker_seeker.modules.organization import schemas as organization_schemas
from speaker_seeker.modules.event import schemas as event_schemas
from beanie import PydanticObjectId
from icecream import ic
from fastui.forms import fastui_form, SelectSearchResponse
from pydantic import BaseModel, Field

import pathlib
from . import application_page

router = APIRouter()
logger = logging.getLogger(settings.LOG_NAME)


@router.post(path='/organization', response_model=FastUI, response_model_exclude_none=True)
async def create_organization_form(
    form: Annotated[organization_schemas.OrganizationCreate, fastui_form(organization_schemas.OrganizationCreate)]
):
    # await organization_service.create(**form.dict())
    await organization_service.create(organization_in=form)
    return [c.FireEvent(event=GoToEvent(url='/organization'))]


@router.get(path='/organization/create', response_model=FastUI, response_model_exclude_none=True)
def form_content():
    return application_page(
        c.ModelForm(
            model=organization_schemas.OrganizationCreate,
            display_mode='page',
            submit_url='/ui/organization'
        ),
        title="Create Organization"
    )


@router.get(path="/organization", response_model=FastUI, response_model_exclude_none=True)
async def organization_table() -> list[AnyComponent]:
    organizations = await organization_service.get_many(fetch_links=True)
    return application_page(
        c.Table(
            data=organizations,
            columns=[
                DisplayLookup(field='name', on_click=GoToEvent(url='/organization/{_id}')),
                DisplayLookup(field='url', mode=DisplayMode.plain),
                DisplayLookup(field='event_count', mode=DisplayMode.plain),
                DisplayLookup(field='agent_count', mode=DisplayMode.plain),
                DisplayLookup(field='speaker_count', mode=DisplayMode.plain),
                DisplayLookup(field='sponsor_count', mode=DisplayMode.plain),
            ],
            data_model=organization_service.Organization
        ),
        c.Link(
            components=[c.Text(text='Create New Organization')],
            on_click=GoToEvent(url="/organization/create")
        ),
        title="Organizations"
    )


@router.get(path="/organization/search", response_model=SelectSearchResponse)
async def search_view(q: str) -> SelectSearchResponse:
    organizations = await organization_service.search_by_name(partial_name=q)
    organization_options = [{'label': organization.name, 'value': str(organization.id)} for organization in organizations]

    options = [
        {'label': "Organization", 'options': organization_options}
    ]
    ic(options)
    return SelectSearchResponse(options=options)


@router.get(path="/organization/{organization_id}", response_model=FastUI, response_model_exclude_none=True, include_in_schema=False)
async def organization_detail(organization_id: PydanticObjectId) -> list[AnyComponent]:
    """
    organization page, the frontend will fetch this when the user visits `/organization/{id}/`.
    """
    organization = await organization_service.get_by_id(organization_id, fetch_links=True)

    event_links = []
    speaker_links = []
    agent_links = []
    sponsor_links = []

    for event in organization.events:
        e = await event.fetch()
        event_links.append(
            c.Link(components=[c.Text(text=e.name)], on_click=GoToEvent(url=f'/event/{e.id}'))
        )

    for agent in organization.agents:
        a = await agent.fetch()
        agent_links.append(
            c.Link(components=[c.Text(text=a.full_name)], on_click=GoToEvent(url=f'/agent/{a.id}'))
        )

    for speaker in organization.speakers:
        s = await speaker.fetch()
        speaker_links.append(
            c.Link(components=[c.Text(text=a.full_name)], on_click=GoToEvent(url=f'/speaker/{s.id}'))
        )

    for sponsor in organization.sponsors:
        s = await sponsor.fetch()
        sponsor_links.append(
            c.Link(components=[c.Text(text=a.name)], on_click=GoToEvent(url=f'/sponsor/{s.id}'))
        )

    return application_page(
        c.Link(components=[c.Text(text='Back')], on_click=BackEvent()),
        c.Div(
            components=[
                c.Heading(text='Details', level=2),
                c.Details(
                    data=organization,
                    fields=[
                        DisplayLookup(field='name'),
                        DisplayLookup(field='url'),
                    ]
                ),
                c.Heading(text='Events', level=2),
                c.Div(
                    components=[
                        c.LinkList(links=event_links)
                    ],
                    class_name='mb-4'
                ),
                c.Heading(text='Agents', level=2),
                c.Div(
                    components=[
                        c.LinkList(links=agent_links)
                    ],
                    class_name='mb-4'
                ),
            ],
            class_name='mb-4'
        ),

    )
