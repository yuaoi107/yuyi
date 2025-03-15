from typing import Annotated

from fastapi import APIRouter, Query, UploadFile, status
from fastapi.responses import StreamingResponse

from src.core.constants import CommonMessage
from src.models.podcast import PodcastCreate, PodcastPublic, PodcastUpdate
from src.services.podcast_service import PodcastServiceDep, PodcastServiceLoginDep

router = APIRouter(tags=["播客"])


@router.post("/users/me/podcasts", status_code=status.HTTP_201_CREATED, response_model=PodcastPublic, summary="为当前用户创建播客")
async def post_user_me_podcast(podcast_service: PodcastServiceLoginDep, podcast_upload: PodcastCreate):
    return podcast_service.create_podcast_by_author_id(podcast_service.user_login.id, podcast_upload)


@router.get("/users/me/podcasts", status_code=status.HTTP_201_CREATED, response_model=list[PodcastPublic], summary="获取当前用户播客列表")
async def get_user_me_podcasts(podcast_service: PodcastServiceLoginDep, offset: Annotated[int, Query()] = 0, limit: Annotated[int, Query()] = 10):
    return podcast_service.get_podcasts_by_author_id(podcast_service.user_login.id, offset, limit)


@router.post("/users/{user_id}/podcasts", status_code=status.HTTP_201_CREATED, response_model=PodcastPublic, summary="为用户创建播客")
async def post_user_podcast(podcast_service: PodcastServiceLoginDep, user_id: int, podcast_upload: PodcastCreate):
    return podcast_service.create_podcast_by_author_id(user_id, podcast_upload)


@router.get("/users/{user_id}/podcasts", status_code=status.HTTP_200_OK, response_model=list[PodcastPublic], summary="获取用户播客列表")
async def get_user_podcasts(podcast_service: PodcastServiceDep, user_id: int, offset: Annotated[int | None, Query()] = 0, limit: Annotated[int | None, Query()] = 10):
    return podcast_service.get_podcasts_by_author_id(user_id, offset, limit)


@router.post("/podcasts", status_code=status.HTTP_201_CREATED, response_model=PodcastPublic, summary="创建播客")
async def post_podcast_with_query(podcast_service: PodcastServiceLoginDep, author_id: Annotated[int, Query], podcast_upload: PodcastCreate):
    return podcast_service.create_podcast_by_author_id(author_id, podcast_upload)


@router.get("/podcasts", status_code=status.HTTP_200_OK, response_model=list[PodcastPublic], summary="获取播客列表")
async def get_podcasts(podcast_service: PodcastServiceDep, offset: Annotated[int | None, Query()] = 0, limit: Annotated[int | None, Query()] = 10):
    return podcast_service.get_all_podcasts(offset, limit)


@router.get("/podcasts/{id}", status_code=status.HTTP_200_OK, response_model=PodcastPublic, summary="获取指定播客")
async def get_user_by_path(podcast_service: PodcastServiceDep, id: int):
    return podcast_service.get_podcast_by_id(id)


@router.put("/podcasts/{id}", status_code=status.HTTP_200_OK, response_model=PodcastPublic, summary="修改指定播客")
async def put_podcast_by_path(podcast_service: PodcastServiceLoginDep, id: int, podcast_update: PodcastUpdate):
    return podcast_service.update_podcast_by_id(id, podcast_update)


@router.delete("/podcasts/{id}", status_code=status.HTTP_200_OK, response_model=CommonMessage, summary="删除指定播客")
async def delete_podcast_by_path(podcast_service: PodcastServiceLoginDep, id: int):
    return podcast_service.delete_podcast_by_id(id)


@router.get("/podcasts/{id}/cover", status_code=status.HTTP_200_OK, response_class=StreamingResponse, summary="获取指定播客封面")
async def get_podcast_cover(podcast_service: PodcastServiceDep, id: int):
    return podcast_service.get_cover_by_id(id)


@router.put("/podcasts/{id}/cover", status_code=status.HTTP_200_OK, response_model=CommonMessage, summary="修改指定播客封面")
async def put_podcast_cover(podcast_service: PodcastServiceLoginDep, id: int, avatar_update: UploadFile):
    return podcast_service.update_cover_by_id(id, avatar_update)


@router.get("/podcasts/{id}/rss", status_code=status.HTTP_200_OK, summary="获取指定播客RSS")
async def get_podcast_cover(podcast_service: PodcastServiceDep, id: int):
    return podcast_service.get_rss_by_id(id)
