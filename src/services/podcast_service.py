

from datetime import date
from fastapi import HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlmodel import Session, select

from src.common.util import delete_file_from_contents, save_file_to_contents
from src.models.podcast import Podcast, PodcastPublic, PodcastUpdate, PodcastUpload
from src.models.user import User
from ..config.settings import settings
from ..common.constants import Message, ContentFileType


class PodcastService:
    @staticmethod
    def create_podcast(session: Session, author_id: int, podcast_upload: PodcastUpload) -> PodcastPublic:
        user_db = session.get(User, author_id)
        if not user_db:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found.")
        if session.exec(select(Podcast).where(Podcast.title == podcast_upload.title)).first():
            raise HTTPException(status.HTTP_409_CONFLICT, "Title taken.")

        extra_data = {
            "author_id": user_db.id,
            "feed_url": "fake",
            "link": "fake",
            "itunes_author": user_db.nickname,
            "itunes_image_url": "fake",
            "createtime": date.today().isoformat(),
            "generator": settings.GENERATOR_TITLE
        }

        new_podcast = Podcast.model_validate(podcast_upload, update=extra_data)
        session.add(new_podcast)
        session.commit()
        session.refresh(new_podcast)

        return new_podcast

    @staticmethod
    def get_user_podcasts(session: Session, author_id: int, offset: int, limit: int) -> list[PodcastPublic]:
        return session.exec(select(Podcast).where(Podcast.author_id == author_id)).all()

    @staticmethod
    def get_podcasts(session: Session, offset: int, limit: int) -> list[PodcastPublic]:
        return session.exec(select(Podcast)).all()

    @staticmethod
    def get_podcast(session: Session, podcast_id: int) -> Podcast:
        db_podcast = session.get(Podcast, podcast_id)
        if not db_podcast:
            raise HTTPException(404, "Podcast not found.")
        return db_podcast

    @staticmethod
    def update_podcast(session: Session, podcast_id: int, podcast_update: PodcastUpdate) -> PodcastPublic:
        podcast_db = PodcastService.get_podcast(session, podcast_id)
        podcast_db.sqlmodel_update(
            podcast_update.model_dump(exclude_unset=True))

    @staticmethod
    def delete_podcast(session: Session, podcast_id: int) -> Message:
        podcast_db = PodcastService.get_podcast(session, podcast_id)
        session.delete(podcast_db)
        session.commit()
        return Message("Podcast deleted.")

    @staticmethod
    def get_podcast_cover(session: Session, podcast_id: int) -> FileResponse:
        podcast_db = PodcastService.get_podcast(session, podcast_id)
        if not podcast_db.itunes_image_url:
            raise HTTPException(404, "Cover not found.")
        return FileResponse(podcast_db.itunes_image_path)

    @staticmethod
    async def update_podcast_cover(session: Session, podcast_id: int, avatar_update: UploadFile) -> Message:
        podcast_db = PodcastService.get_podcast(session, podcast_id)
        if podcast_db.itunes_image_path:
            delete_file_from_contents(podcast_db.itunes_image_path)
        podcast_db.itunes_image_path = await save_file_to_contents(avatar_update, ContentFileType.PODCAST_COVER)
        return Message(detail="Cover changed.")
