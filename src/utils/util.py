import os
import uuid
from enum import Enum

from fastapi import UploadFile
from passlib.context import CryptContext
from pydantic import BaseModel

from ..config.settings import settings


class FileType(Enum):
    AVATAR = "avatars"
    PODCAST_COVER = "podcast_covers"
    EPISODE_COVER = "episode_covers"
    AUDIO = "audios"
    RSS_XML = "rss_xmls"


class Message(BaseModel):
    detail: str


def add_responses(*status_codes: int) -> dict[int, dict[str, Message]]:
    error_message = {"model": Message}
    responses = {}
    for code in status_codes:
        responses[code] = error_message
    return responses


def hash_password(password: str) -> str:
    encrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return encrypt_context.hash(password)


async def archive_file(file: UploadFile, filetype: FileType) -> str:
    try:
        ext = file.filename.split(".")[-1]

        unique_filename = f"{uuid.uuid4().hex}.{ext}"

        dest_dir = os.path.join(settings.ARCHIVES_DIR, filetype.value)

        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)

        file_path = os.path.join(
            dest_dir,
            unique_filename
        )

        with open(file_path, 'wb') as f:
            contents = await file.read()
            f.write(contents)

        return "/".join([settings.BASE_URL + settings.ARCHIVE_ENDPOINT, filetype.value, unique_filename])

    except Exception as e:
        raise
    finally:
        await file.close()


def delete_by_url(url: str):
    filepath = settings.ARCHIVES_DIR + "/" + "/".join(url.split("/")[-2:])
    os.remove(filepath)
