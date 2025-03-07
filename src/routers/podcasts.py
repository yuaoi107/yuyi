from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse

from ..core.constants import UserRole
from ..core.auth import UserDep
from ..services.crud.podcast_service import PodcastService
from ..database.database import SessionDep
from ..core.util import add_responses, Message
from ..models.podcast import (
    PodcastCreate,
    PodcastPublic,
    PodcastUpdate
)

router = APIRouter(
    tags=["播客"]
)


@router.post(
    "/users/me/podcasts",
    status_code=status.HTTP_201_CREATED,
    response_model=PodcastPublic,
    summary="为当前用户创建播客",
    responses=add_responses(401)
)
async def post_user_me_podcast(user_login: UserDep, session: SessionDep, podcast_upload: PodcastCreate):
    return PodcastService.create_podcast(session, user_login.id, podcast_upload)


@router.get(
    "/users/me/podcasts",
    status_code=status.HTTP_201_CREATED,
    response_model=list[PodcastPublic],
    summary="获取当前用户播客列表",
    responses=add_responses(401)
)
async def get_user_me_podcasts(
    user_login: UserDep,
    session: SessionDep,
    offset: Annotated[int, Query()] = 0,
    limit: Annotated[int, Query()] = 10
):
    return PodcastService.get_user_podcasts(session, user_login.id, offset, limit)


@router.post(
    "/users/{user_id}/podcasts",
    status_code=status.HTTP_201_CREATED,
    response_model=PodcastPublic,
    summary="为用户创建播客",
    responses=add_responses(401, 403, 404, 409)
)
async def post_user_podcast(
    user_login: UserDep,
    session: SessionDep,
    user_id: int,
    podcast_upload: PodcastCreate
):
    if user_login.role != UserRole.ADMIN.value and user_login.id != user_id:
        raise HTTPException(403)
    return PodcastService.create_podcast(session, user_id, podcast_upload)


@router.get(
    "/users/{user_id}/podcasts",
    status_code=status.HTTP_200_OK,
    response_model=list[PodcastPublic],
    summary="获取用户播客列表"
)
async def get_user_podcasts(
    session: SessionDep,
    user_id: int,
    offset: Annotated[int | None, Query()] = 0,
    limit: Annotated[int | None, Query()] = 10
):
    return PodcastService.get_user_podcasts(session, user_id, offset, limit)


@router.post(
    "/podcasts",
    status_code=status.HTTP_201_CREATED,
    response_model=PodcastPublic,
    summary="创建播客",
    responses=add_responses(401, 403, 404, 409)
)
async def post_podcast_with_query(
    user_login: UserDep,
    session: SessionDep,
    author_id: Annotated[int, Query],
    podcast_upload: PodcastCreate
):
    if user_login.role != UserRole.ADMIN.value and user_login.id != author_id:
        raise HTTPException(403)
    return PodcastService.create_podcast(session, author_id, podcast_upload)


@router.get(
    "/podcasts",
    status_code=status.HTTP_200_OK,
    response_model=list[PodcastPublic],
    summary="获取播客列表"
)
async def get_podcasts(
    session: SessionDep,
    offset: Annotated[int | None, Query()] = 0,
    limit: Annotated[int | None, Query()] = 10
):
    return PodcastService.get_podcasts(session, offset, limit)


@router.get(
    "/podcasts/{podcast_id}",
    status_code=status.HTTP_200_OK,
    response_model=PodcastPublic,
    summary="获取指定播客",
    responses=add_responses(404)
)
async def get_user_by_path(session: SessionDep, podcast_id: int):
    return PodcastService.get_podcast(session, podcast_id)


@router.put(
    "/podcasts/{podcast_id}",
    status_code=status.HTTP_200_OK,
    response_model=PodcastPublic,
    summary="修改指定播客",
    responses=add_responses(401, 403, 404, 409)
)
async def put_podcast_by_path(user_login: UserDep, session: SessionDep, podcast_id: int, podcast_update: PodcastUpdate):
    podcast_to_update = PodcastService.get_podcast(session, podcast_id)
    if user_login.role != UserRole.ADMIN.value and user_login.id != podcast_to_update.author_id:
        raise HTTPException(403)
    return PodcastService.update_podcast(session, podcast_id, podcast_update)


@router.delete(
    "/podcasts/{podcast_id}",
    status_code=status.HTTP_200_OK,
    response_model=Message,
    summary="删除指定播客",
    responses=add_responses(401, 403, 404, 409)
)
async def delete_podcast_by_path(user_login: UserDep, session: SessionDep, podcast_id: int):
    podcast_to_update = PodcastService.get_podcast(session, podcast_id)
    if user_login.role != UserRole.ADMIN.value and user_login.id != podcast_to_update.author_id:
        raise HTTPException(403)
    return PodcastService.delete_podcast(session, podcast_id)


@router.get(
    "/podcasts/{podcast_id}/cover",
    status_code=status.HTTP_200_OK,
    response_class=FileResponse,
    summary="获取指定播客封面",
    responses=add_responses(404)
)
async def get_podcast_cover(session: SessionDep, podcast_id: int):
    return PodcastService.get_podcast_cover(session, podcast_id)


@router.put(
    "/podcasts/{podcast_id}/cover",
    status_code=status.HTTP_200_OK,
    response_model=Message,
    summary="修改指定播客封面",
    responses=add_responses(401, 403, 404)
)
async def put_podcast_cover(user_login: UserDep, session: SessionDep, podcast_id: int, avatar_update: UploadFile):
    podcast_to_update = PodcastService.get_podcast(session, podcast_id)
    if user_login.role != UserRole.ADMIN.value and user_login.id != podcast_to_update.author_id:
        raise HTTPException(403)
    return await PodcastService.update_podcast_cover(session, podcast_id, avatar_update)
