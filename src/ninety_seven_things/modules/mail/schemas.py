# Standard Library Imports
import pathlib

# 3rd-Party Imports
from pydantic import BaseModel


class AttachmentCreate(BaseModel):
    raw_contents: bytes
    file_type: str
    source_file_name: pathlib.Path
    destination_file_name: str
    content_id: str
