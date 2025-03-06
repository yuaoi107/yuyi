

from datetime import date
from fastapi import HTTPException, status
from sqlmodel import Session, select

from src.models.podcast import Podcast, PodcastPublic, PodcastUpload
from src.models.user import User
from ..config.settings import settings


class PodcastService:
    # @staticmethod
    # def _get_feed_url(podcast_id: int) -> str:
    #     return

    @staticmethod
    def create_podcast(session: Session, author_id: int, podcast: PodcastUpload) -> PodcastPublic:

        if session.exec(select(Podcast).where(Podcast.title == podcast.title)).first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Title taken.")

        author = session.get(User, author_id)

        extra_data = {
            "author_id": author_id,
            "feed_url": "fake",
            "link": "fake",
            "itunes_author": author.nickname,
            "itunes_image_url": "fake",
            "createtime": date.today().isoformat(),
            "generator": settings.GENERATOR_TITLE
        }

        db_podcast = Podcast.model_validate(podcast, update=extra_data)
        session.add(db_podcast)
        session.commit()
        session.refresh(db_podcast)

        return db_podcast

    @staticmethod
    def get_podcasts(session: Session, offset: int, limit: int) -> list[PodcastPublic]:
        return session.exec(select(Podcast)).all()

    @staticmethod
    def get_podcast(session: Session, id: int) -> PodcastPublic:
        db_podcast = session.get(Podcast, id)
        if not db_podcast:
            raise HTTPException(404, "Podcast not found.")
        return db_podcast

    @staticmethod
    def update_podcast(session: Session, id: int) -> PodcastPublic:
        pass
