# Standard Library Imports
import logging

# 3rd-Party Imports
from fastapi import APIRouter
from fastui import AnyComponent, FastUI
from fastui import components as c
from icecream import ic

# Application-Local Imports
from ninety_seven_things.core.config import settings

# Local Folder Imports
from . import admin_page

router = APIRouter()
logger = logging.getLogger(settings.LOG_NAME)


@router.get(path="/", response_model=FastUI, response_model_exclude_none=True)
def api_index() -> list[AnyComponent]:
    # language=markdown
    markdown = """\
This site provides an in-progress demo of 97 Things

"""
    return admin_page(c.Markdown(text=markdown))
