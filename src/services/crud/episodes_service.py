from time import time
from email.utils import formatdate
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlmodel import Session, select

from ...common.constants import UserRole
from ...common.auth import UserDep
from ...services.crud.podcast_service import PodcastService
from ...database.database import SessionDep
from ...common.util import add_responses, Message, delete_file_from_contents, save_file_to_contents
from ...models.episode import (
    Episode,
    EpisodeUpload,
    EpisodePublic,
    EpisodeUpdate
)


class EpisodeService:

    @staticmethod
    def get_episode(session: Session, episode_id: int) -> Episode:
        episode_db = session.get(Episode, episode_id)
        if not episode_db:
            raise HTTPException(404, "Episode not found.")
        return episode_db

    @staticmethod
    def get_episodes(session: Session, offset: int, limit: int) -> list[Episode]:
        return session.exec(select(Episode)).all()

    @staticmethod
    def get_podcast_episodes(session: Session, podcast_id: int, offset: int, limit: int) -> list[Episode]:
        return session.exec(select(Episode).where(Episode.podcast_id == podcast_id)).all()

    @staticmethod
    def create_episode(session: Session, podcast_id: int, episode_upload: EpisodeUpload) -> Episode:
        podcast_db = PodcastService.get_podcast(session, podcast_db)

        episode_existed = session.exec(select(Episode).where(
            Episode.podcast_id == podcast_id, Episode.title == episode_upload.title)).first()

        if episode_existed:
            raise HTTPException(409, "Title taken.")

        extra_data = {
            "podcast_id": podcast_id,
            "guid": uuid4(),
            "pub_date": formatdate(time())
        }

        new_episode = Episode.model_validate(episode_upload, update=extra_data)
        session.add(new_episode)
        session.commit(new_episode)
        session.refresh(new_episode)
        return new_episode

    @staticmethod
    def update_episode(session: Session, episode_id: int, episode_upload: EpisodeUpload) -> Episode:

        episode_db = EpisodeService.get_episode(
            session, episode_id)

        episode_db.sqlmodel_update(
            episode_upload.model_dump(exclude_unset=True))
        session.add(episode_db)
        session.commit()
        session.refresh(episode_db)
        return episode_db

    @staticmethod
    def delete_episode(session: Session, episode_id: int) -> Message:
        episode_db = EpisodeService.get_episode(session, episode_id)
        session.delete(episode_db)
        session.commit()
        return Message(detail="Episode deleted.")

    @staticmethod
    def get_episode_cover(session: Session, episode_id: int) -> FileResponse:
        episode_db = EpisodeService.get_episode(session, episode_id)
        if not episode_db.itunes_image_path:
            raise HTTPException(404, "Cover not found.")
        return FileResponse(episode_db.itunes_image_path)

    @staticmethod
    async def update_episode_cover(session: Session, episode_id: int, cover_update: UploadFile) -> Message:
        episode_db = EpisodeService.get_episode(session, episode_id)
        try:
            if episode_db.itunes_image_path:
                delete_file_from_contents(episode_db.itunes_image_path)
            episode_db.itunes_image_path = await save_file_to_contents(cover_update)
        except:
            raise HTTPException(500, "Cover change failed.")

        session.add(episode_db)
        session.commit()
        return Message(detail="Cover changed.")

    @staticmethod
    def get_episode_audio(session: Session, episode_id: int) -> FileResponse:
        episode_db = EpisodeService.get_episode(session, episode_id)
        if not episode_db.enclosure_path:
            raise HTTPException(404, "Audio not found.")
        return FileResponse(episode_db.itunes_image_path)

    @staticmethod
    async def update_episode_audio(session: Session, episode_id: int, audio_update: UploadFile) -> Message:
        episode_db = EpisodeService.get_episode(session, episode_id)
        try:
            if episode_db.enclosure_path:
                delete_file_from_contents(episode_db.enclosure_path)
            episode_db.enclosure_path = await save_file_to_contents(audio_update)
        except:
            raise HTTPException(500, "Audio change failed.")

        session.add(episode_db)
        session.commit()
        return Message(detail="Audio changed.")
