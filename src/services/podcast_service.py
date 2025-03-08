from datetime import date
from fastapi import UploadFile
from fastapi.responses import FileResponse
from sqlmodel import Session, select

from src.config.settings import settings
from src.models.episode import Episode
from src.models.user import User
from src.models.podcast import Podcast, PodcastUpdate, PodcastCreate
from src.services.rss_service import RSSService
from src.services.utils import save_file_to_contents, delete_file_from_contents
from src.core.constants import CommonMessage, ContentFileType, UserRole
from src.core.exceptions import (
    PodcastCoverNotFoundException,
    NoPermissionException,
    PodcastFeedNotFoundException,
    PodcastNotFoundException,
    UserNotFoundException,
    PodcastTitleAlreadyExistsException
)


class PodcastService:

    def __init__(self, session: Session, user_login: User | None = None):
        self.session = session
        self.user_login = user_login
        self.rss_service = RSSService()

    def create_podcast_by_author_id(self, author_id: int, podcast_upload: PodcastCreate) -> Podcast:
        if self.user_login.id != author_id and self.user_login.role != UserRole.ADMIN.value:
            raise NoPermissionException()

        author = self._get_user_by_id(author_id)

        same_name_podcast = self.session.exec(
            select(Podcast).where(Podcast.title == podcast_upload.title)
        ).first()
        if same_name_podcast:
            raise PodcastTitleAlreadyExistsException()

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
            raise PodcastNotFoundException()

        return podcast

    def update_podcast_by_id(self, id: int, podcast_update: PodcastUpdate) -> Podcast:
        podcast = self.get_podcast_by_id(id)
        if self.user_login.id != podcast.author_id and self.user_login.role != UserRole.ADMIN.value:
            raise NoPermissionException()

        same_name_podcast = self.session.exec(
            select(Podcast).where(Podcast.title == podcast_update.title)
        ).first()
        if same_name_podcast:
            raise PodcastTitleAlreadyExistsException()

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
            raise NoPermissionException()

        self._delete_existing_cover(podcast)
        self.rss_service._delete_existing_rss_xml()

        for episode in podcast.episodes:
            self._delete_episode(episode)

        self.session.delete(podcast)
        self.session.commit()

        return CommonMessage(message="Podcast Deleted.")

    def get_cover_by_id(self, id: int) -> FileResponse:
        podcast = self.get_podcast_by_id(id)

        if not podcast.itunes_image_path:
            raise PodcastCoverNotFoundException()

        return FileResponse(podcast.itunes_image_path)

    async def update_cover_by_id(self, id: int, avatar_update: UploadFile) -> CommonMessage:
        podcast = self.get_podcast_by_id(id)
        if self.user_login.id != podcast.author_id and self.user_login.role != UserRole.ADMIN.value:
            raise NoPermissionException()

        self._delete_existing_cover(podcast)
        podcast.itunes_image_path = await save_file_to_contents(avatar_update, ContentFileType.PODCAST_COVER)

        self.session.add(podcast)
        self.session.commit()

        return CommonMessage(message="Cover Changed.")

    def get_rss_by_id(self, id: int) -> FileResponse:

        podcast = self.get_podcast_by_id(id)

        if not podcast.feed_path:
            raise PodcastFeedNotFoundException()

        return FileResponse(podcast.feed_path)

    def _get_user_by_id(self, user_id):
        user = self.session.get(User, user_id)
        if not user:
            raise UserNotFoundException()

        return user

    def _delete_existing_cover(self, podcast: Podcast) -> None:
        if podcast.itunes_image_path:
            delete_file_from_contents(podcast.itunes_image_path)

    def _delete_episode(self, episode: Episode) -> None:
        if episode.itunes_image_path:
            delete_file_from_contents(episode.itunes_image_path)
        if episode.enclosure_path:
            delete_file_from_contents(episode.enclosure_path)

        self.session.delete(episode)
