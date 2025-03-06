from datetime import date
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status
from sqlmodel import select

from ..utils.dependables import SessionDep
from ..utils.util import hash_password, add_responses, Message
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


@router.post("", status_code=status.HTTP_201_CREATED, response_model=PodcastPublic, summary="创建播客",
             responses=add_responses(409))
async def create_podcast(session: SessionDep, podcast: PodcastUpload):

    if session.exec(select(Podcast).where(Podcast.title == podcast.title)).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Title taken.")
