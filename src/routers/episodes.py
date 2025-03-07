from datetime import date
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlmodel import select

from src.services.crud.episodes_service import EpisodeService

from ..common.constants import UserRole
from ..common.auth import UserDep
from ..services.crud.podcast_service import PodcastService
from ..database.database import SessionDep
from ..common.util import add_responses, Message
from ..models.episode import (
    Episode,
    EpisodeCreate,
    EpisodePublic,
    EpisodeUpdate
)

router = APIRouter(
    tags=["单集"]
)


@router.post(
    "/episodes",
    status_code=status.HTTP_201_CREATED,
    response_model=EpisodePublic,
    summary="创建单集",
    responses=add_responses(401, 403, 404, 409)
)
async def post_episode_with_query(
    user_login: UserDep,
    session: SessionDep,
    podcast_id: Annotated[int, Query()],
    episode_upload: EpisodeCreate
):
    if user_login.role != UserRole.ADMIN.value and PodcastService.get_podcast(session, podcast_id).author_id != user_login.id:
        raise HTTPException(403)
    return EpisodeService.create_episode(session, podcast_id, episode_upload)


@router.get(
    "/episodes",
    status_code=status.HTTP_200_OK,
    response_model=list[EpisodePublic],
    summary="获取单集列表"
)
async def get_episodes(
    session: SessionDep,
    offset: Annotated[int, Query()] = 0,
    limit: Annotated[int, Query()] = 10
):
    return EpisodeService.get_episodes(session, offset, limit)


@router.get(
    "/episodes/{episode_id}",
    status_code=status.HTTP_200_OK,
    response_model=EpisodePublic,
    summary="获取指定单集",
    responses=add_responses(404)
)
async def get_episode_by_path(
    session: SessionDep,
    episode_id: int
):
    return EpisodeService.get_episode(session, episode_id)


@router.put(
    "/episodes/{episode_id}",
    status_code=status.HTTP_200_OK,
    response_model=EpisodePublic,
    summary="修改指定单集",
    responses=add_responses(401, 403, 404, 409)
)
async def put_episode_by_path(
    user_login: UserDep,
    session: SessionDep,
    episode_id: int,
    episode_update: EpisodeCreate
):
    episode_to_update = EpisodeService.get_episode(session, episode_id)
    if user_login.role != UserRole.ADMIN.value and \
            PodcastService.get_podcast(session, episode_to_update.podcast_id).author_id != user_login.id:
        raise HTTPException(403)
    return EpisodeService.update_episode(session, episode_id, episode_update)


@router.delete(
    "/episodes/{episode_id}",
    status_code=status.HTTP_200_OK,
    response_model=Message,
    summary="删除指定单集",
    responses=add_responses(401, 403, 404, 409)
)
async def delete_episode_by_path(
    user_login: UserDep,
    session: SessionDep,
    episode_id: int,
):
    episode_to_update = EpisodeService.get_episode(session, episode_id)
    if user_login.role != UserRole.ADMIN.value and \
            PodcastService.get_podcast(session, episode_to_update.podcast_id).author_id != user_login.id:
        raise HTTPException(403)
    return EpisodeService.delete_episode(session, episode_id)


@router.get(
    "/episodes/{episode_id}/cover",
    status_code=status.HTTP_200_OK,
    response_class=FileResponse,
    summary="获取指定单集封面",
    responses=add_responses(404)
)
async def get_episode_cover(session: SessionDep, episode_id: int):
    return EpisodeService.get_episode_cover(session, episode_id)


@router.put(
    "/episodes/{episode_id}/cover",
    status_code=status.HTTP_200_OK,
    response_model=Message,
    summary="修改指定单集封面",
    responses=add_responses(401, 403, 404, 409)
)
async def put_episode_cover(user_login: UserDep, session: SessionDep, episode_id: int, cover_update: UploadFile):
    episode_to_update = EpisodeService.get_episode(session, episode_id)
    if user_login.role != UserRole.ADMIN.value and \
            PodcastService.get_podcast(session, episode_to_update.podcast_id).author_id != user_login.id:
        raise HTTPException(403)
    return await EpisodeService.update_episode_cover(session, episode_id, cover_update)


@router.get(
    "/episodes/{episode_id}/audio",
    status_code=status.HTTP_200_OK,
    response_class=FileResponse,
    summary="获取指定单集音频",
    responses=add_responses(404)
)
async def get_episode_cover(session: SessionDep, episode_id: int):
    return EpisodeService.get_episode_audio(session, episode_id)


@router.put(
    "/episodes/{episode_id}/audio",
    status_code=status.HTTP_200_OK,
    response_model=Message,
    summary="修改指定单集音频",
    responses=add_responses(401, 403, 404, 409)
)
async def put_episode_cover(user_login: UserDep, session: SessionDep, episode_id: int, audio_update: UploadFile):
    episode_to_update = EpisodeService.get_episode(session, episode_id)
    if user_login.role != UserRole.ADMIN.value and \
            PodcastService.get_podcast(session, episode_to_update.podcast_id).author_id != user_login.id:
        raise HTTPException(403)
    return await EpisodeService.update_episode_cover(session, episode_id, audio_update)


@router.get(
    "/podcasts/{podcast_id}/episodes",
    status_code=status.HTTP_200_OK,
    response_model=list[EpisodePublic],
    summary="获取指定播客单集列表",
    responses=add_responses(404)
)
async def get_podcast_episodes(session: SessionDep, podcast_id: int):
    return EpisodeService.get_podcast_episodes(session, podcast_id)


@router.post(
    "/podcasts/{podcast_id}/episodes",
    status_code=status.HTTP_201_CREATED,
    response_model=EpisodePublic,
    summary="获取指定播客单集列表",
    responses=add_responses(401, 403, 404, 409)
)
async def post_podcast_episode(
    user_login: UserDep,
    session: SessionDep,
    podcast_id: int,
    episode_upload: EpisodeCreate
):
    if user_login.role != UserRole.ADMIN.value and PodcastService.get_podcast(session, podcast_id).author_id != user_login.id:
        raise HTTPException(403)
    return EpisodeService.create_episode(session, podcast_id, episode_upload)
