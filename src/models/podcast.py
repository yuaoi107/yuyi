from typing import TYPE_CHECKING, Optional

from sqlmodel import Relationship, SQLModel, Field
from datetime import date

if TYPE_CHECKING:
    from .user import User, UserPublic


class PodcastBase(SQLModel):

    title: str
    description: str
    language: str
    itunes_category: str
    itunes_subcategory: str | None = None
    itunes_explicit: bool = False

    copyright: str


class Podcast(PodcastBase, table=True):

    id: int | None = Field(default=None, primary_key=True)
    author_id: int | None = Field(default=None, foreign_key="user.id")
    itunes_image_url: str
    feed_url: str
    link: str
    itunes_author: str
    itunes_block: bool = False
    itunes_complete: bool = False
    generator: str

    author: Optional["User"] = Relationship(back_populates="podcasts")


class PodcastUpload(PodcastBase):
    pass


class PodcastPublic(PodcastBase):
    id: int
    author_id: int
    itunes_image_url: str
    feed_url: str
    createtime: date
    itunes_complete: bool = False
    createtime: date
    generator: str


class PodcastPublicWithAuthor(PodcastPublic):
    author: Optional["User"] = None


class PodcastPatch(PodcastBase):
    itunes_complete: bool | None = None
