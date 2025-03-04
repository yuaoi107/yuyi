from datetime import date
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status
from sqlmodel import select

from ..utils.dependables import SessionDep
from ..utils.util import hash_password, add_responses, Message
from ..models.user import (
    User,
    UserUpload,
    UserPublic,
    UserPatch
)

router = APIRouter(
    prefix="/users",
    tags=["用户"]
)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=UserPublic, summary="创建用户",
             responses=add_responses(409))
async def create_user(session: SessionDep, user: UserUpload):

    if session.exec(select(User).where(User.username == user.username)).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Username taken.")

    if session.exec(select(User).where(User.nickname == user.nickname)).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Nickname taken.")

    hashed_password = hash_password(user.password)
    extra_data = {
        "hashed_password": hashed_password,
        "createtime": date.today().isoformat()
    }
    db_user = User.model_validate(user, update=extra_data)

    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@router.get("", status_code=status.HTTP_200_OK, response_model=list[UserPublic], summary="获取用户")
async def get_users(session: SessionDep, offset: Annotated[int, Query()], limit: Annotated[int, Query()]):
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return users


@router.patch("{id}", status_code=status.HTTP_200_OK, response_model=UserPublic, summary="修改用户",
              responses=add_responses(404))
async def patch_user(session: SessionDep, id: int, user: UserPatch):

    db_user = session.get(User, id)

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Not found user.")

    user_data = user.model_dump(exclude_unset=True)
    extra_data = {}

    if "password" in user_data:
        hashed_password = hash_password(user_data["password"])
        extra_data["hashed_password"] = hashed_password

    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user


@router.delete("{id}", status_code=status.HTTP_200_OK, response_model=Message, summary="删除用户", responses=add_responses(404))
async def delete_user(session: SessionDep, id: int):

    user = session.get(User, id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found.")
    session.delete(user)
    return {"detail": "Successfully deleted"}
