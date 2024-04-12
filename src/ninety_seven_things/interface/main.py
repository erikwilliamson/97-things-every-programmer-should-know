from fastui import FastUI, AnyComponent, components as c
from fastapi import APIRouter
import logging
from ninety_seven_things.core.config import settings
from . import application_page
router = APIRouter()
logger = logging.getLogger(settings.LOG_NAME)

@router.get(path='/', response_model=FastUI, response_model_exclude_none=True)
def api_index() -> list[AnyComponent]:
    # language=markdown
    markdown = """\
This site provides an in-progress demo of 97 Things

"""
    return application_page(c.Markdown(text=markdown))
