from sqlmodel import SQLModel, Field
from pydantic import EmailStr
from datetime import date


class UserBase(SQLModel):
    nickname: str
    email: EmailStr | None = None
    description: str | None = None


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str
    hashed_password: str
    avatar_url: str | None = None
    createtime: date


class UserUpload(UserBase):
    username: str
    password: str


class UserPublic(UserBase):
    id: int
    avatar_url: str | None = None
    createtime: date


class UserPatch(UserBase):
    password: str | None = None
