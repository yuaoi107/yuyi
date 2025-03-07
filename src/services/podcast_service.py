from datetime import date
from fastapi import UploadFile
from fastapi.responses import FileResponse
from sqlmodel import Session, select

from src.models.episode import Episode
from src.models.user import User
from src.services.util import save_file_to_contents, delete_file_from_contents
from src.models.podcast import Podcast, PodcastUpdate, PodcastCreate
from src.config.settings import settings
from src.core.constants import Message, ContentFileType, UserRole
from src.core.exceptions import (
    CoverNotFoundException,
    NoPermissionException,
    PodcastNotFoundException,
    UserNotFoundException,
    NameAlreadyExistsException
)


class PodcastService:

    def __init__(self, session: Session, user_login: User | None = None):
        self.session = session
        self.user_login = user_login

    def create_podcast_by_author_id(self, author_id: int, podcast_upload: PodcastCreate) -> Podcast:

        if self.user_login.id != author_id and self.user_login.role != UserRole.ADMIN.value:
            raise NoPermissionException()

        author = self._get_user_by_id(author_id)

        same_name_podcast = self.session.exec(
            select(Podcast).where(Podcast.title == podcast_upload.title)
        ).first()
        if same_name_podcast:
            raise NameAlreadyExistsException()

        extra_data = {
            "author_id": author.id,
            "itunes_author": author.nickname,
            "createtime": date.today().isoformat(),
            "generator": settings.GENERATOR_TITLE
        }

        new_podcast = Podcast.model_validate(podcast_upload, update=extra_data)
        self.session.add(new_podcast)
        self.session.commit()
        self.session.refresh(new_podcast)

        return new_podcast

    def get_podcasts_by_author_id(self, author_id: int, offset: int, limit: int) -> list[Podcast]:

        return self.session.exec(
            select(Podcast).where(Podcast.author_id == author_id)
        ).all()

    def get_all_podcasts(self, offset: int, limit: int) -> list[Podcast]:

        return self.session.exec(select(Podcast)).all()

    def get_podcast_by_id(self, id: int) -> Podcast:

        podcast = self.session.get(Podcast, id)
        if not podcast:
            raise PodcastNotFoundException()

        return podcast

    def update_podcast_by_id(self, id: int, podcast_update: PodcastUpdate) -> Podcast:

        podcast = self.get_podcast_by_id(id)
        if self.user_login.id != podcast.author_id and self.user_login.role != UserRole.ADMIN.value:
            raise NoPermissionException()

        podcast.sqlmodel_update(podcast_update.model_dump(exclude_unset=True))
        self.session.add(podcast)
        self.session.commit()

        return podcast

    def delete_podcast_by_id(self, id: int) -> Message:

        podcast = self.get_podcast_by_id(id)
        if self.user_login.id != podcast.author_id and self.user_login.role != UserRole.ADMIN.value:
            raise NoPermissionException()

        self._delete_existing_cover(podcast)

        for episode in podcast.episodes:
            self._delete_episode(episode)

        self.session.delete(podcast)
        self.session.commit()

        return Message("Podcast deleted.")

    def get_cover_by_id(self, id: int) -> FileResponse:

        podcast = self.get_podcast_by_id(id)

        if not podcast.itunes_image_path:
            raise CoverNotFoundException()

        return FileResponse(podcast.itunes_image_path)

    async def update_cover_by_id(self, id: int, avatar_update: UploadFile) -> Message:

        podcast = self.get_podcast_by_id(id)
        if self.user_login.id != podcast.author_id and self.user_login.role != UserRole.ADMIN.value:
            raise NoPermissionException()

        self._delete_existing_cover(podcast)
        podcast.itunes_image_path = await save_file_to_contents(avatar_update, ContentFileType.PODCAST_COVER)

        self.session.add(podcast)
        self.session.commit()

        return Message(detail="Cover changed.")

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
