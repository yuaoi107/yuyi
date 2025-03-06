from typing import TYPE_CHECKING, Optional

from sqlmodel import Relationship, SQLModel, Field
from pydantic import EmailStr
from datetime import date

if TYPE_CHECKING:
    from .podcast import Podcast, PodcastPublic


class UserBase(SQLModel):
    nickname: str = Field(min_length=6, max_length=20)
    email: EmailStr | None = None
    description: str | None = Field(default=None, max_length=200)


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str
    hashed_password: str
    avatar_url: str | None = None
    createtime: date

    podcasts: list["Podcast"] = Relationship(back_populates="author")


class UserUpload(UserBase):
    username: str = Field(min_length=6, max_length=20)
    password: str = Field(min_length=6, max_length=20)


class UserPublic(UserBase):
    id: int
    username: str
    avatar_url: str | None = None
    createtime: date


class UserPublicWithPodcasts(UserPublic):
    podcasts: list["PodcastPublic"] = []


class UserPatch(SQLModel):
    nickname: str | None = Field(default=None, min_length=6, max_length=20)
    email: EmailStr | None = Field(default=None)
    description: str | None = Field(default=None, max_length=200)
    password: str | None = Field(default=None, min_length=6, max_length=20)
