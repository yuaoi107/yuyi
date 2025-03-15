from datetime import date
from typing import Annotated
from fastapi import Depends, UploadFile
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select

from src.core.auth import UserDep
from src.core.database import SessionDep
from src.services.cos_service import CosService, CosServiceDep
from src.config.settings import settings
from src.models.episode import Episode
from src.models.user import User
from src.models.podcast import Podcast, PodcastUpdate, PodcastCreate
from src.services.rss_service import RssService, RssServiceDep
from src.core.constants import CommonMessage, UserRole
from src.core.exceptions import (
    PodcastCoverNotFoundError,
    NoPermissionError,
    PodcastFeedNotFoundError,
    PodcastNotFoundError,
    UserNotFoundError,
    PodcastTitleAlreadyExistsError
)
from src.utils.file_utils import get_unique_filename


class PodcastService:

    def __init__(self, session: Session, cos_service: CosService, rss_service: RssService, user_login: User | None = None):
        self.session = session
        self.cos_service = cos_service
        self.rss_service = rss_service
        self.user_login = user_login

    def create_podcast_by_author_id(self, author_id: int, podcast_upload: PodcastCreate) -> Podcast:
        if self.user_login.id != author_id and self.user_login.role != UserRole.ADMIN.value:
            raise NoPermissionError()

        author = self._get_user_by_id(author_id)

        same_name_podcast = self.session.exec(
            select(Podcast).where(Podcast.title == podcast_upload.title)
        ).first()
        if same_name_podcast:
            raise PodcastTitleAlreadyExistsError()

        extra_data = {
            "author_id": author.id,
            "itunes_author": author.nickname,
            "createtime": date.today().isoformat(),
            "generator": settings.GENERATOR_NAME
        }

        new_podcast = Podcast.model_validate(podcast_upload, update=extra_data)
        self.session.add(new_podcast)
        self.session.commit()
        self.session.refresh(new_podcast)

        self.rss_service.update_podcast_rss(new_podcast)
        self.session.commit()
        self.session.refresh(new_podcast)

        return new_podcast

    def get_podcasts_by_author_id(self, author_id: int, offset: int, limit: int) -> list[Podcast]:
        return self.session.exec(select(Podcast).where(Podcast.author_id == author_id).offset(offset).limit(limit)).all()

    def get_all_podcasts(self, offset: int, limit: int) -> list[Podcast]:
        return self.session.exec(select(Podcast).offset(offset).limit(limit)).all()

    def get_podcast_by_id(self, id: int) -> Podcast:
        podcast = self.session.get(Podcast, id)
        if not podcast:
            raise PodcastNotFoundError()

        return podcast

    def update_podcast_by_id(self, id: int, podcast_update: PodcastUpdate) -> Podcast:
        podcast = self.get_podcast_by_id(id)
        if self.user_login.id != podcast.author_id and self.user_login.role != UserRole.ADMIN.value:
            raise NoPermissionError()

        same_name_podcast = self.session.exec(
            select(Podcast).where(Podcast.title == podcast_update.title)
        ).first()
        if same_name_podcast:
            raise PodcastTitleAlreadyExistsError()

        podcast.sqlmodel_update(podcast_update.model_dump(exclude_unset=True))
        self.session.add(podcast)
        self.session.commit()
        self.session.refresh(podcast)

        self.rss_service.update_podcast_rss(podcast)
        self.session.commit()
        self.session.refresh(podcast)

        return podcast

    def delete_podcast_by_id(self, id: int) -> CommonMessage:
        podcast = self.get_podcast_by_id(id)
        if self.user_login.id != podcast.author_id and self.user_login.role != UserRole.ADMIN.value:
            raise NoPermissionError()

        self._delete_existing_cover(podcast)
        self._delete_existing_rss_xml(podcast)

        for episode in podcast.episodes:
            self._delete_episode(episode)

        self.session.delete(podcast)
        self.session.commit()

        return CommonMessage(message="Podcast Deleted.")

    def get_cover_by_id(self, id: int) -> StreamingResponse:
        podcast = self.get_podcast_by_id(id)

        if not podcast.itunes_image_path:
            raise PodcastCoverNotFoundError()

        return StreamingResponse(self.cos_service.fetch_file(podcast.itunes_image_path))

    def update_cover_by_id(self, id: int, avatar_update: UploadFile) -> CommonMessage:
        podcast = self.get_podcast_by_id(id)
        if self.user_login.id != podcast.author_id and self.user_login.role != UserRole.ADMIN.value:
            raise NoPermissionError()

        self._delete_existing_cover(podcast)

        cover_filename = self._get_cover_filename(
            podcast.author.id, podcast.id, avatar_update.filename)
        self.cos_service.save_file(avatar_update.file, cover_filename)
        podcast.itunes_image_path = cover_filename

        self.session.add(podcast)
        self.session.commit()

        return CommonMessage(message="Cover Changed.")

    def get_rss_by_id(self, id: int) -> StreamingResponse:

        podcast = self.get_podcast_by_id(id)

        if not podcast.feed_path:
            raise PodcastFeedNotFoundError()

        return StreamingResponse(self.cos_service.fetch_file(podcast.feed_path))

    def _get_cover_filename(self, author_id: int, podcast_id: int, original_filename: str) -> str:

        return f"users/{author_id}/podcasts/{podcast_id}/cover/{get_unique_filename(original_filename)}"

    def _get_user_by_id(self, user_id):
        user = self.session.get(User, user_id)
        if not user:
            raise UserNotFoundError()

        return user

    def _delete_existing_cover(self, podcast: Podcast) -> None:
        if podcast.itunes_image_path:
            self.cos_service.delete_file(podcast.itunes_image_path)

    def _delete_existing_rss_xml(self, podcast: Podcast) -> None:
        if podcast.feed_path:
            self.cos_service.delete_file(podcast.feed_path)

    def _delete_episode(self, episode: Episode) -> None:
        if episode.itunes_image_path:
            self.cos_service.delete_file(episode.itunes_image_path)
        if episode.enclosure_path:
            self.cos_service.delete_file(episode.enclosure_path)

        self.session.delete(episode)


def get_podcast_service(session: SessionDep, cos_service: CosServiceDep, rss_service: CosServiceDep):
    return PodcastService(session, cos_service, rss_service)


def get_podcast_service_with_login(session: SessionDep, cos_service: CosServiceDep, rss_service: RssServiceDep, user_login: UserDep):
    return PodcastService(session, cos_service, rss_service, user_login)


PodcastServiceDep = Annotated[PodcastService, Depends(get_podcast_service)]
PodcastServiceLoginDep = Annotated[PodcastService, Depends(
    get_podcast_service_with_login)]
