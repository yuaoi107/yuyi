from datetime import date
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status
from sqlmodel import select

from ..common.auth import UserDep
from ..services.podcast_service import PodcastService
from ..services.shared import get_target_user_id

from ..database.database import SessionDep
from ..common.util import add_responses, Message
from ..models.podcast import (
    Podcast,
    PodcastUpload,
    PodcastPublic,
    PodcastPatch
)

router = APIRouter(
    prefix="/podcasts",
    tags=["播客"]
)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=PodcastPublic,
    summary="创建播客",
    responses=add_responses(401, 403, 409)
)
async def post(
    user_login: UserDep,
    session: SessionDep,
    podcast: PodcastUpload,
    user_id: Annotated[int | None, Query()] = None
):

    target_user_id = get_target_user_id(user_login, user_id)
    return PodcastService.create_podcast(session, target_user_id, podcast)


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=list[PodcastPublic],
    summary="获取播客列表"
)
async def get_with_query(
    session: SessionDep,
    offset: Annotated[int | None, Query()] = 0,
    limit: Annotated[int | None, Query()] = 10
):
    return PodcastService.get_podcasts(session, offset, limit)
