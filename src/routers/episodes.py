from datetime import date
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlmodel import select

from ..common.constants import UserRole
from ..common.auth import UserDep
from ..services.crud.podcast_service import PodcastService
from ..database.database import SessionDep
from ..common.util import add_responses, Message
from ..models.episode import (
    Episode,
    EpisodeUpload,
    EpisodePublic,
    EpisodeUpdate
)

router = APIRouter(
    tags=["播客"]
)
