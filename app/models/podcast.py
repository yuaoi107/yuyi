from sqlmodel import SQLModel, Field
from datetime import date

class PodcastBase(SQLModel):

    title: str
    description: str
    language: str
    itunes_category: str
    itunes_sub_category: str | None = None
    itunes_explicit: bool = False

    copyright: str 

class Podcast(PodcastBase, table=True):

    id: int | None = Field(default=None, primary_key=True)
    author_id: int | None = Field(default=None, foreign_key="user.id")
    itunes_image_url: str
    feed_url: str
    link: str
    itunes_author: str
    createtime: date
    itunes_block: bool = False
    itunes_complete: bool = False
    generator: str

class PodcastUpload(PodcastBase):
    pass

class PodcastPublic(PodcastBase):
    id: int
    author_id: int
    itunes_image_url: str
    feed_url: str
    link: str
    createtime: date
    itunes_complete: bool = False
    generator: str

class PodcastPatch(PodcastBase):
    link: str | None = None
    itunes_complete: bool | None = None
    