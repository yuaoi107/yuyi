from typing import Optional, TYPE_CHECKING
from sqlmodel import Relationship, SQLModel, Field
from datetime import datetime

if TYPE_CHECKING:
    from .podcast import Podcast


class EpisodeBase(SQLModel):
    title: str
    description: str
    itunes_episode: int
    itunes_season: int


class Episode(EpisodeBase, table=True):

    id: int | None = Field(default=None, primary_key=True)

    podcast_id: int | None = Field(default=None, foreign_key="podcast.id")
    podcast: Optional["Podcast"] = Relationship(back_populates="episodes")
    guid: str

    enclosure_path: str | None = None
    enclosure_length: int | None = None
    enclosure_type: str | None = None

    pub_date: str
    itunes_duration: int | None = None
    link: str | None = None

    itunes_image_path: str | None = None
    itunes_explicit: bool = False
    block: bool = False
    is_complete: bool = False


class EpisodeUpload(EpisodeBase):
    pass


class EpisodePublic(EpisodeBase):
    id: int
    pub_date: datetime


class EpisodeUpdate(EpisodeBase):
    pass
