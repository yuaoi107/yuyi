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


@router.get("/test")
async def get():
    return True
