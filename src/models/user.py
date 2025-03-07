from typing import TYPE_CHECKING, Optional

from sqlmodel import Relationship, SQLModel, Field
from pydantic import EmailStr
from datetime import date

from ..core.constants import UserRole

if TYPE_CHECKING:
    from .podcast import Podcast, PodcastPublic


class UserBase(SQLModel):
    nickname: str
    email: EmailStr | None = None
    description: str | None = None


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str
    hashed_password: str
    avatar_path: str | None = None
    createtime: date
    role: str | None = UserRole.USER.value

    podcasts: list["Podcast"] = Relationship(back_populates="author")


class UserCreate(UserBase):
    username: str
    password: str


class UserPublic(UserBase):
    id: int
    username: str
    createtime: date
    role: str


class UserPublicWithPodcasts(UserPublic):
    podcasts: list["PodcastPublic"] = []


class UserUpdate(SQLModel):
    nickname: str | None = None
    email: EmailStr | None = None
    description: str | None = None
    password: str | None = None
