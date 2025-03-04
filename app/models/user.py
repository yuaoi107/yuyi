from sqlmodel import SQLModel, Field
from pydantic import EmailStr
from datetime import date


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


class UserUpload(UserBase):
    username: str = Field(min_length=6, max_length=20)
    password: str = Field(min_length=6, max_length=20)


class UserPublic(UserBase):
    id: int
    username: str
    avatar_url: str | None = None
    createtime: date


class UserPatch(UserBase):
    password: str | None = None
