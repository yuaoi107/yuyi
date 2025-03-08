from enum import Enum

from pydantic import BaseModel


class UserRole(Enum):
    ADMIN = "admin"
    USER = "user"


class ContentFileType(Enum):
    AVATAR = "avatars"
    PODCAST_COVER = "podcast_covers"
    EPISODE_COVER = "episode_covers"
    AUDIO = "audios"
    RSS_XML = "rss_xmls"


class CommonMessage(BaseModel):
    message: str
