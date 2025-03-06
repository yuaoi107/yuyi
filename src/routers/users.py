from typing import Annotated

from fastapi import APIRouter, Query, status, HTTPException

from ..database.database import SessionDep
from ..common.util import add_responses, Message, UserRole
from ..common.auth import UserDep
from ..models.user import (
    User,
    UserUpload,
    UserPublic,
    UserPatch
)
from ..services.user_service import UserService

router = APIRouter(
    prefix="/users",
    tags=["用户"]
)


def same_role_check(user_login: User, id):
    if user_login.role != UserRole.ADMIN and user_login.id != id:
        raise HTTPException(403)


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
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=UserPublic,
    summary="获取用户",
    responses=add_responses(404)
)
async def get_by_path(session: SessionDep, id: int):
    return UserService.get_user(session, id)


@router.patch(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=UserPublic,
    summary="修改用户",
    responses=add_responses(404, 409)
)
async def patch_by_path(user_login: UserDep, session: SessionDep, id: int, user: UserPatch):
    same_role_check(user_login, id)
    return UserService.update_user(session, id, user)


@router.delete(
    "/{id}",
    status_code=status.HTTP_200_OK,
    response_model=Message,
    summary="删除用户",
    responses=add_responses(404)
)
async def delete_by_path(user_login: UserDep, session: SessionDep, id: int):
    same_role_check(user_login, id)
    return UserService.delete_user(session, id)


# @router.get(
#     "/me",
#     status_code=status.HTTP_200_OK,
#     response_model=UserPublic,
#     summary="获取当前用户",
#     responses=add_responses(401)
# )
# async def get_user_me(user: UserDep):
#     return UserService.get_me(user)
