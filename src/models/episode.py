from typing import Optional, TYPE_CHECKING
from sqlmodel import Relationship, SQLModel, Field

if TYPE_CHECKING:
    from src.models.podcast import Podcast


class EpisodeBase(SQLModel):
    title: str
    description: str | None = None


class Episode(EpisodeBase, table=True):

    id: int | None = Field(default=None, primary_key=True)
    podcast_id: int = Field(foreign_key="podcast.id")
    podcast: Optional["Podcast"] = Relationship(back_populates="episodes")
    guid: str
    enclosure_path: str | None = None
    enclosure_length: int | None = None
    enclosure_type: str | None = None

    pub_date: str | None = None
    itunes_duration: int | None = None
    link: str | None = None
    itunes_image_path: str | None = None
    itunes_explicit: bool = False
    block: bool = False
    is_complete: bool = False


class EpisodeCreate(EpisodeBase):
    pass


class EpisodePublic(EpisodeBase):

    id: int
    pub_date: str | None


class EpisodeUpdate(EpisodeBase):

    title: str | None = None
    description: str | None = None
