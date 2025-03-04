from sqlmodel import SQLModel, Field
from datetime import datetime

class EpisodeBase(SQLModel):
    title: str
    description: str
    itunes_episode: int
    itunes_season: int

class Episode(EpisodeBase, table=True):

    id: int | None = Field(default=None, primary_key=True)

    guid: str

    enclosure_url: str
    enclosure_length: int
    enclosure_type: str

    pub_date: datetime
    itunes_duration: int
    link: str

    itunes_image_url: str
    itunes_explicit: bool = False
    block: bool = False

class EpisodeUpload(EpisodeBase):
    pass

class EpisodePublic(EpisodeBase):
    id: int
    pub_date: datetime

class EpisodePatch(EpisodeBase):
    pass