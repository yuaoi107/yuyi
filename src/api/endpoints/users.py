from typing import Annotated

from fastapi import APIRouter, Query, UploadFile, status
from fastapi.responses import FileResponse, StreamingResponse

from src.core.constants import CommonMessage
from src.models.user import UserCreate, UserPublic, UserUpdate
from src.services.user_service import UserServiceDep, UserServiceLoginDep

router = APIRouter(prefix="/users", tags=["用户"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=UserPublic, summary="创建用户")
async def post_user(user_service: UserServiceDep, user: UserCreate):
    return user_service.create_user(user)


@router.get("", status_code=status.HTTP_200_OK, response_model=list[UserPublic], summary="获取用户列表")
async def get_users_with_query(user_service: UserServiceDep, offset: Annotated[int, Query()] = 0, limit: Annotated[int, Query()] = 10):
    return user_service.get_all_users(offset, limit)


@router.get("/me", status_code=status.HTTP_200_OK, response_model=UserPublic, summary="获取当前用户")
async def get_user_me(user_service: UserServiceLoginDep):
    return user_service.user_login


@router.put("/me", status_code=status.HTTP_200_OK, response_model=UserPublic, summary="修改当前用户")
async def put_user_me(user_service: UserServiceLoginDep, user_update: UserUpdate):
    return user_service.update_user_by_id(user_service.user_login.id, user_update)


@router.delete("/me", status_code=status.HTTP_200_OK, response_model=CommonMessage, summary="删除当前用户")
async def delete_user_me(user_service: UserServiceLoginDep):
    return user_service.delete_user_by_id(user_service.user_login.id)


@router.put("/me/avatar", status_code=status.HTTP_200_OK, response_model=CommonMessage, summary="修改当前用户头像")
async def put_user_me_avatar(user_service: UserServiceLoginDep, avatar_update: UploadFile):
    return user_service.update_avatar_by_id(user_service.user_login.id, avatar_update)


@router.get("/me/avatar", status_code=status.HTTP_200_OK, response_class=FileResponse, summary="获取当前用户头像")
async def get_user_me_avatar(user_service: UserServiceLoginDep):
    return user_service.get_avatar_by_id(user_service.user_login.id)


@router.get("/{id}", status_code=status.HTTP_200_OK, response_model=UserPublic, summary="获取指定用户")
async def get_user_by_path(user_service: UserServiceDep, id: int):
    return user_service.get_user_by_id(id)


@router.put("/{id}", status_code=status.HTTP_200_OK, response_model=UserPublic, summary="修改指定用户")
async def put_user_by_path(user_service: UserServiceLoginDep, id: int, user_update: UserUpdate):
    return user_service.update_user_by_id(id, user_update)


@router.delete("/{id}", status_code=status.HTTP_200_OK, response_model=CommonMessage, summary="删除指定用户")
async def delete_user_by_path(user_service: UserServiceLoginDep, id: int):
    return user_service.delete_user_by_id(id)


@router.get("/{id}/avatar", status_code=status.HTTP_200_OK, response_class=StreamingResponse, summary="获取指定用户头像")
async def get_user_avatar_by_path(user_service: UserServiceDep, id: int):
    return user_service.get_avatar_by_id(id)


@router.put("/{id}/avatar", status_code=status.HTTP_200_OK, response_model=CommonMessage, summary="修改指定用户头像")
async def put_user_avatar_by_path(user_service: UserServiceLoginDep, id: int, avatar_update: UploadFile):
    return user_service.update_avatar_by_id(id, avatar_update)
