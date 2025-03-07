from typing import TYPE_CHECKING, Optional

from sqlmodel import Relationship, SQLModel, Field
from datetime import date

if TYPE_CHECKING:
    from .user import User, UserPublic
    from .episode import Episode


class PodcastBase(SQLModel):

    title: str
    description: str
    language: str
    itunes_category: str
    itunes_subcategory: str | None = None
    itunes_explicit: bool = False

    copyright: str = "Copyleft."


class Podcast(PodcastBase, table=True):

    id: int | None = Field(default=None, primary_key=True)
    author_id: int | None = Field(default=None, foreign_key="user.id")
    itunes_image_path: str | None = None
    feed_path: str | None = None
    link: str | None = None
    itunes_author: str
    itunes_block: bool = False
    itunes_complete: bool = False
    generator: str
    createtime: date
    is_complete: bool = False
    is_published: bool = False

    author: Optional["User"] = Relationship(back_populates="podcasts")
    episodes: list["Episode"] = Relationship(back_populates="podcast")


class PodcastUpload(PodcastBase):
    pass


class PodcastPublic(PodcastBase):
    id: int
    author_id: int
    createtime: date
    itunes_complete: bool
    createtime: date
    generator: str
    is_complete: bool
    is_published: bool


class PodcastPublicWithAuthor(PodcastPublic):
    author: Optional["User"] = None


class PodcastUpdate(SQLModel):

    title: str | None = None
    description: str | None = None
    language: str | None = None
    itunes_category: str | None = None
    itunes_subcategory: str | None = None
    itunes_explicit: bool = False

    copyright: str | None = None
    itunes_complete: bool | None = None
    published: bool | None = None
