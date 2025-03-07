from datetime import date
from fastapi import HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlmodel import Session, select

from ...services.crud.episodes_service import EpisodeService
from ...common.util import delete_file_from_contents, save_file_to_contents
from ...models.podcast import Podcast, PodcastUpdate, PodcastUpload
from ...services.crud.user_service import UserService
from ...config.settings import settings
from ...common.constants import Message, ContentFileType


class PodcastService:
    @staticmethod
    def create_podcast(session: Session, author_id: int, podcast_upload: PodcastUpload) -> Podcast:
        user_db = UserService.get_user(session, author_id)

        if session.exec(select(Podcast).where(Podcast.title == podcast_upload.title)).first():
            raise HTTPException(status.HTTP_409_CONFLICT, "Title taken.")

        extra_data = {
            "author_id": user_db.id,
            "itunes_author": user_db.nickname,
            "createtime": date.today().isoformat(),
            "generator": settings.GENERATOR_TITLE
        }

        new_podcast = Podcast.model_validate(podcast_upload, update=extra_data)
        session.add(new_podcast)
        session.commit()
        session.refresh(new_podcast)

        return new_podcast

    @staticmethod
    def get_user_podcasts(session: Session, author_id: int, offset: int, limit: int) -> list[Podcast]:
        return session.exec(select(Podcast).where(Podcast.author_id == author_id)).all()

    @staticmethod
    def get_podcasts(session: Session, offset: int, limit: int) -> list[Podcast]:
        return session.exec(select(Podcast)).all()

    @staticmethod
    def get_podcast(session: Session, podcast_id: int) -> Podcast:
        db_podcast = session.get(Podcast, podcast_id)
        if not db_podcast:
            raise HTTPException(404, "Podcast not found.")
        return db_podcast

    @staticmethod
    def update_podcast(session: Session, podcast_id: int, podcast_update: PodcastUpdate) -> Podcast:
        podcast_db = PodcastService.get_podcast(session, podcast_id)
        podcast_db.sqlmodel_update(
            podcast_update.model_dump(exclude_unset=True))
        session.add(podcast_db)
        session.commit()
        return podcast_db

    @staticmethod
    def delete_podcast(session: Session, podcast_id: int) -> Message:
        podcast_db = PodcastService.get_podcast(session, podcast_id)
        UserService.delete_user_avatar(podcast_db)
        for episode in podcast_db.episodes:
            EpisodeService.delete_episode(session, episode.id)
        session.delete(podcast_db)
        session.commit()
        return Message("Podcast deleted.")

    @staticmethod
    def get_podcast_cover(session: Session, podcast_id: int) -> FileResponse:
        podcast_db = PodcastService.get_podcast(session, podcast_id)
        if not podcast_db.itunes_image_path:
            raise HTTPException(404, "Cover not found.")
        return FileResponse(podcast_db.itunes_image_path)

    @staticmethod
    async def update_podcast_cover(session: Session, podcast_id: int, avatar_update: UploadFile) -> Message:
        podcast_db = PodcastService.get_podcast(session, podcast_id)
        try:
            PodcastService.delete_podcast(podcast_db)
            podcast_db.itunes_image_path = await save_file_to_contents(avatar_update, ContentFileType.PODCAST_COVER)
        except Exception:
            raise HTTPException(500, "Cover change failed.")

        session.add(podcast_db)
        session.commit()

        return Message(detail="Cover changed.")

    @staticmethod
    async def delete_podcast_cover(podcast: Podcast):
        if podcast.itunes_image_path:
            delete_file_from_contents(podcast.itunes_image_path)
