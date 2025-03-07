import os
import uuid

from fastapi import UploadFile


from ..config.settings import settings
from .constants import Message, ContentFileType


def add_responses(*status_codes: int) -> dict[int, dict[str, Message]]:
    message = {"model": Message}
    responses = {500: message}
    for code in status_codes:
        responses[code] = message
    return responses


async def save_file_to_contents(file: UploadFile, content_filetype: ContentFileType) -> str:
    try:
        ext = file.filename.split(".")[-1]
        unique_filename = f"{uuid.uuid4().hex}.{ext}"

        dest_dir = os.path.join(settings.CONTENTS_DIR, content_filetype.value)

        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)

        file_path = os.path.join(dest_dir, unique_filename)

        with open(file_path, 'wb') as f:
            contents = await file.read()
            f.write(contents)

        return file_path

    except Exception as e:
        raise
    finally:
        await file.close()


def delete_file_from_contents(file_path: str):
    os.remove(file_path)
