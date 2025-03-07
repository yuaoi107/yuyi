from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Query, UploadFile, status
from fastapi.responses import FileResponse

from src.common.constants import UserRole

from ..database.database import SessionDep
from ..common.util import add_responses, Message
from ..common.auth import UserDep
from ..models.user import (
    UserUpload,
    UserPublic,
    UserUpdate
)
from ..services.user_service import UserService

router = APIRouter(
    prefix="/users",
    tags=["用户"]
)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=UserPublic, summary="创建用户",
    responses=add_responses(409)
)
async def post_user(session: SessionDep, user: UserUpload):
    return UserService.create_user(session, user)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=list[UserPublic],
    summary="获取用户列表"
)
async def get_users_with_query(
    session: SessionDep,
    offset: Annotated[int, Query()] = 0,
    limit: Annotated[int, Query()] = 10
):
    return UserService.get_users(session, offset, limit)


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=UserPublic,
    summary="获取当前用户",
    responses=add_responses(401)
)
async def get_user_me(user_login: UserDep):
    return user_login


@router.put(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=UserPublic,
    summary="修改当前用户",
    responses=add_responses(401)
)
async def put_user_me(user_login: UserDep, session: SessionDep, user_update: UserUpdate):
    return UserService.update_user(session, user_login.id, user_update)


@router.delete(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=Message,
    summary="删除当前用户",
    responses=add_responses(401)
)
async def delete_user_me(user_login: UserDep, session: SessionDep):
    return UserService.delete_user(session, user_login.id)


@router.put(
    "/me/avatar",
    status_code=status.HTTP_200_OK,
    response_model=Message,
    summary="修改当前用户头像",
    responses=add_responses(401)
)
async def put_user_me_avatar(user_login: UserDep, session: SessionDep, avatar_update: UploadFile):
    return await UserService.update_user_avatar(session, user_login.id, avatar_update)


@router.get(
    "/me/avatar",
    status_code=status.HTTP_200_OK,
    response_class=FileResponse,
    summary="获取当前用户头像",
    responses=add_responses(401)
)
async def get_user_me_avatar(user_login: UserDep, session: SessionDep):
    return UserService.get_user_avatar(session, user_login.id)


@router.get(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserPublic,
    summary="获取用户",
    responses=add_responses(404)
)
async def get_user_by_path(session: SessionDep, user_id: int):
    return UserService.get_user(session, user_id)


@router.put(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserPublic,
    summary="修改用户",
    responses=add_responses(401, 403, 404, 409)
)
async def put_user_by_path(user_login: UserDep, session: SessionDep, user_id: int, user_update: UserUpdate):
    if user_login.role != UserRole.ADMIN and user_login.id != user_id:
        raise HTTPException(403)
    return UserService.update_user(session, user_id, user_update)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=Message,
    summary="删除用户",
    responses=add_responses(401, 403, 404)
)
async def delete_user_by_path(user_login: UserDep, session: SessionDep, user_id: int):
    if user_login.role != UserRole.ADMIN and user_login.id != user_id:
        raise HTTPException(403)
    return UserService.delete_user(session, user_id)


@router.get(
    "/{user_id}/avatar",
    status_code=status.HTTP_200_OK,
    response_class=FileResponse,
    summary="获取用户头像",
    responses=add_responses(404)
)
async def get_user_avatar_by_path(session: SessionDep, user_id: int):
    return UserService.get_user_avatar(session, user_id)


@router.put(
    "/{user_id}/avatar",
    status_code=status.HTTP_200_OK,
    response_model=Message,
    summary="修改用户头像",
    responses=add_responses(401, 403, 404)
)
async def put_user_avatar_by_path(user_login: UserDep, session: SessionDep, user_id: int, avatar_update: UploadFile):
    if user_login.role != UserRole.ADMIN and user_login.id != user_id:
        raise HTTPException(403)
    return UserService.update_user_avatar(session, user_id, avatar_update)
