from typing import Annotated

from fastapi import APIRouter, Path, Query, status

from ..database.database import SessionDep
from ..common.util import add_responses, Message
from ..common.auth import UserDep
from ..models.user import (
    UserUpload,
    UserPublic,
    UserPatch
)
from ..services.user_service import UserService
from ..services.shared import check_permission

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
async def post(session: SessionDep, user: UserUpload):
    return UserService.create_user(session, user)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=list[UserPublic],
    summary="获取用户列表"
)
async def get_with_query(
    session: SessionDep,
    offset: Annotated[int, Query()] = 0,
    limit: Annotated[int, Query()] = 10
):
    return UserService.get_users(session, offset, limit)


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    response_model=UserPublic,
    summary="当前用户",
    responses=add_responses(401)
)
async def get_me(user_login: UserDep):
    return user_login


@router.get(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=UserPublic,
    summary="获取用户",
    responses=add_responses(404)
)
async def get_by_path(session: SessionDep, id: int | None = None):
    return UserService.get_user(session, id)


@router.patch(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=UserPublic,
    summary="修改用户",
    responses=add_responses(401, 403, 404, 409)
)
async def patch_by_path(user_login: UserDep, session: SessionDep, id: int, user: UserPatch):
    check_permission(user_login, id)
    return UserService.update_user(session, id, user)


@router.delete(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=Message,
    summary="删除用户",
    responses=add_responses(401, 403, 404)
)
async def delete_by_path(user_login: UserDep, session: SessionDep, id: int):
    check_permission(user_login, id)
    return UserService.delete_user(session, id)
