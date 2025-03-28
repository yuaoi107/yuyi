from typing import Annotated

from fastapi import APIRouter, Query, UploadFile, status
from fastapi.responses import FileResponse

from src.core.constants import CommonMessage
from src.models.episode import EpisodeCreate, EpisodePublic, EpisodeUpdate
from src.services.episodes_service import EpisodeServiceDep, EpisodeServiceLoginDep

router = APIRouter(tags=["单集"])


@router.post("/episodes", status_code=status.HTTP_201_CREATED, response_model=EpisodePublic, summary="创建单集")
async def post_episode_with_query(episode_service: EpisodeServiceLoginDep, podcast_id: Annotated[int, Query()], episode_upload: EpisodeCreate):
    return episode_service.create_episode_by_podcast_id(podcast_id, episode_upload)


@router.get("/episodes", status_code=status.HTTP_200_OK, response_model=list[EpisodePublic], summary="获取单集列表")
async def get_episodes(episode_service: EpisodeServiceDep, offset: Annotated[int, Query()] = 0, limit: Annotated[int, Query()] = 10):
    return episode_service.get_all_episodes(offset, limit)


@router.get("/episodes/{id}", status_code=status.HTTP_200_OK, response_model=EpisodePublic, summary="获取指定单集")
async def get_episode_by_path(episode_service: EpisodeServiceDep, id: int):
    return episode_service.get_episode_by_id(id)


@router.put("/episodes/{id}", status_code=status.HTTP_200_OK, response_model=EpisodePublic, summary="修改指定单集")
async def put_episode_by_path(episode_service: EpisodeServiceLoginDep, id: int, episode_update: EpisodeUpdate):
    return episode_service.update_episode_by_id(id, episode_update)


@router.delete("/episodes/{id}", status_code=status.HTTP_200_OK, response_model=CommonMessage, summary="删除指定单集")
async def delete_episode_by_path(episode_service: EpisodeServiceLoginDep, id: int):
    return episode_service.delete_episode_by_id(id)


@router.get("/episodes/{id}/cover", status_code=status.HTTP_200_OK, response_class=FileResponse, summary="获取指定单集封面")
async def get_episode_cover(episode_service: EpisodeServiceDep, id: int):
    return episode_service.get_cover_by_id(id)


@router.put("/episodes/{id}/cover", status_code=status.HTTP_200_OK, response_model=CommonMessage, summary="修改指定单集封面")
async def put_episode_cover(episode_service: EpisodeServiceLoginDep, id: int, cover_update: UploadFile):
    return episode_service.update_cover_by_id(id, cover_update)


@router.get("/episodes/{id}/audio", status_code=status.HTTP_200_OK, response_class=FileResponse, summary="获取指定单集音频")
async def get_episode_cover(episode_service: EpisodeServiceDep, id: int):
    return episode_service.get_audio_by_id(id)


@router.put("/episodes/{id}/audio", status_code=status.HTTP_200_OK, response_model=CommonMessage, summary="修改指定单集音频")
async def put_episode_cover(episode_service: EpisodeServiceLoginDep, id: int, audio_update: UploadFile):
    return episode_service.update_audio_by_id(id, audio_update)


@router.get("/podcasts/{podcast_id}/episodes", status_code=status.HTTP_200_OK, response_model=list[EpisodePublic], summary="获取指定播客单集列表")
async def get_podcast_episodes(episode_service: EpisodeServiceDep, podcast_id: int, offset: Annotated[int, Query()] = 0, limit: Annotated[int, Query] = 10):
    return episode_service.get_episodes_by_podcast_id(podcast_id, offset, limit)


@router.post("/podcasts/{podcast_id}/episodes", status_code=status.HTTP_201_CREATED, response_model=EpisodePublic, summary="为指定播客创建单集")
async def post_podcast_episode(episode_service: EpisodeServiceLoginDep, podcast_id: int, episode_upload: EpisodeCreate):
    return episode_service.create_episode_by_podcast_id(podcast_id, episode_upload)
