# Future Imports
from __future__ import annotations as _annotations

# 3rd-Party Imports
import fastapi
import fastui.forms
import pydantic
from fastapi import params as fastapi_params
from fastui import AnyComponent
from fastui import components as c
from fastui.events import GoToEvent
from icecream import ic

# Application-Local Imports
from ninety_seven_things.core.config import settings


#
# https://github.com/pydantic/FastUI/issues/146
#
def patched_fastui_form(model: type[fastui.forms.FormModel]) -> fastapi_params.Depends:
    async def run_fastui_form(request: fastapi.Request):
        async with request.form() as form_data:
            model_data = fastui.forms.unflatten(form_data)

            try:
                yield model.model_validate(model_data)
            except pydantic.ValidationError as e:
                raise fastapi.HTTPException(
                    status_code=422,
                    detail={"form": e.errors(include_input=False, include_url=False, include_context=False)},
                )

    return fastapi.Depends(run_fastui_form)


def admin_page(*components: AnyComponent, title: str | None = None) -> list[AnyComponent]:
    return [
        c.PageTitle(text=f"{settings.PROJECT_NAME} — {title}" if title else settings.PROJECT_NAME),
        c.Navbar(
            title=settings.PROJECT_NAME,
            title_event=GoToEvent(url="/"),
            start_links=[
                c.Link(
                    components=[c.Text(text="Articles")],
                    on_click=GoToEvent(url="/admin/article"),
                    active="startswith:/admin/article",
                ),
                c.Link(
                    components=[c.Text(text="Authors")],
                    on_click=GoToEvent(url="/admin/author"),
                    active="startswith:/admin/author",
                ),
            ],
        ),
        c.Page(
            components=[
                *((c.Heading(text=title),) if title else ()),
                *components,
            ],
        ),
        c.Footer(
            extra_text=settings.PROJECT_NAME,
            links=[
                c.Link(
                    components=[c.Text(text="GitLab")],
                    on_click=GoToEvent(url="https://gitlab.com/erik_at_ts/speaker-seeker"),
                ),
                c.Link(components=[c.Text(text="PyPI")], on_click=GoToEvent(url="https://pypi.org/project/fastui/")),
                c.Link(components=[c.Text(text="NPM")], on_click=GoToEvent(url="https://www.npmjs.com/org/pydantic/")),
            ],
        ),
    ]
