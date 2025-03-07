from typing import Annotated

from fastapi import APIRouter, Query, UploadFile, status
from fastapi.responses import FileResponse

from src.database.database import SessionDep
from src.core.constants import Message
from src.core.auth import UserDep
from src.models.user import (
    UserCreate,
    UserPublic,
    UserUpdate
)
from src.services.user_service import UserService

router = APIRouter(
    prefix="/users",
    tags=["用户"]
)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=UserPublic, summary="创建用户")
async def post_user(session: SessionDep, user: UserCreate):
    user_service = UserService(session)
    return user_service.create_user(user)


@router.get("", status_code=status.HTTP_200_OK, response_model=list[UserPublic], summary="获取用户列表")
async def get_users_with_query(session: SessionDep, offset: Annotated[int, Query()] = 0, limit: Annotated[int, Query()] = 10):
    user_service = UserService(session)
    return user_service.get_all_users(offset, limit)


@router.get("/me", status_code=status.HTTP_200_OK, response_model=UserPublic, summary="获取当前用户")
async def get_user_me(user_login: UserDep):
    return user_login


@router.put("/me", status_code=status.HTTP_200_OK, response_model=UserPublic, summary="修改当前用户")
async def put_user_me(user_login: UserDep, session: SessionDep, user_update: UserUpdate):
    user_service = UserService(session, user_login)
    return user_service.update_user_by_id(user_login.id, user_update)


@router.delete("/me", status_code=status.HTTP_200_OK, response_model=Message, summary="删除当前用户")
async def delete_user_me(user_login: UserDep, session: SessionDep):
    user_service = UserService(session, user_login)
    return user_service.delete_user_by_id(user_login.id)


@router.put("/me/avatar", status_code=status.HTTP_200_OK, response_model=Message, summary="修改当前用户头像")
async def put_user_me_avatar(user_login: UserDep, session: SessionDep, avatar_update: UploadFile):
    user_service = UserService(session, user_login)
    return await user_service.update_avatar_by_id(user_login.id, avatar_update)


@router.get("/me/avatar", status_code=status.HTTP_200_OK, response_class=FileResponse, summary="获取当前用户头像")
async def get_user_me_avatar(user_login: UserDep, session: SessionDep):
    user_service = UserService(session, user_login)
    return user_service.get_avatar_by_id(user_login.id)


@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=UserPublic, summary="获取指定用户")
async def get_user_by_path(session: SessionDep, id: int):
    user_service = UserService(session)
    return user_service.get_user_by_id(id)


@router.put("/{id}", status_code=status.HTTP_200_OK, response_model=UserPublic, summary="修改指定用户")
async def put_user_by_path(user_login: UserDep, session: SessionDep, id: int, user_update: UserUpdate):
    user_service = UserService(session, user_login)
    return user_service.update_user_by_id(id, user_update)


@router.delete("/{id}", status_code=status.HTTP_200_OK, response_model=Message, summary="删除指定用户")
async def delete_user_by_path(user_login: UserDep, session: SessionDep, id: int):
    user_service = UserService(session, user_login)
    return user_service.delete_user_by_id(id)


@router.get("/{id}/avatar", status_code=status.HTTP_200_OK, response_class=FileResponse, summary="获取指定用户头像")
async def get_user_avatar_by_path(session: SessionDep, id: int):
    user_service = UserService(session)
    return user_service.get_avatar_by_id(id)


@router.put("/{id}/avatar", status_code=status.HTTP_200_OK, response_model=Message, summary="修改指定用户头像")
async def put_user_avatar_by_path(user_login: UserDep, session: SessionDep, id: int, avatar_update: UploadFile):
    user_service = UserService(session, user_login)
    return await user_service.update_avatar_by_id(id, avatar_update)
