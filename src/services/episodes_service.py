from time import time
from email.utils import formatdate
from uuid import uuid4

from fastapi import UploadFile
from fastapi.responses import FileResponse
from sqlmodel import Session, select

from src.core.constants import UserRole
from src.core.constants import Message
from src.services.util import save_file_to_contents, delete_file_from_contents
from src.models.episode import (
    Episode,
    EpisodeCreate,
    EpisodeUpdate
)
from src.core.exceptions import (
    AudioNotFoundException,
    EpisodeNotFoundException,
    NoPermissionException,
    PodcastNotFoundException,
    NameAlreadyExistsException,
    CoverNotFoundException
)
from src.models.podcast import Podcast
from src.models.user import User


class EpisodeService:

    def __init__(self, session: Session, user_login: User):
        self.session = session
        self.user_login = user_login

    def get_episode_by_id(self, id: int) -> Episode:

        episode = self.session.get(Episode, id)
        if not episode:
            raise EpisodeNotFoundException()
        return episode

    def get_all_episodes(self, offset: int, limit: int) -> list[Episode]:

        return self.session.exec(select(Episode)).all()

    def get_episodes_by_podcast_id(self, podcast_id: int, offset: int, limit: int) -> list[Episode]:

        return self.session.exec(
            select(Episode).where(Episode.podcast_id == podcast_id)
        ).all()

    def create_episode_by_podcast_id(self, podcast_id: int, episode_upload: EpisodeCreate) -> Episode:

        podcast = self.session.get(Podcast, podcast_id)
        if not podcast:
            raise PodcastNotFoundException()
        if self.user_login.id != podcast.author_id and self.user_login.role != UserRole.ADMIN.value:
            raise NoPermissionException()

        same_title_episode = self.session.exec(select(Episode).where(
            Episode.podcast_id == podcast_id, Episode.title == episode_upload.title)).first()

        if same_title_episode:
            raise NameAlreadyExistsException()

        extra_data = {
            "podcast_id": podcast_id,
            "guid": uuid4(),
            "pub_date": formatdate(time())
        }

        new_episode = Episode.model_validate(episode_upload, update=extra_data)
        self.session.add(new_episode)
        self.session.commit(new_episode)
        self.session.refresh(new_episode)

        return new_episode

    def update_episode_by_id(self, id: int, episode_upload: EpisodeUpdate) -> Episode:

        episode = self.get_episode_by_id(id)
        podcast = self.session.get(Podcast, episode.podcast_id)
        if self.user_login.id != podcast.author_id and self.user_login.role != UserRole.ADMIN.value:
            raise NoPermissionException()

        episode.sqlmodel_update(
            episode_upload.model_dump(exclude_unset=True)
        )
        self.session.add(episode)
        self.session.commit()
        self.session.refresh(episode)
        return episode

    def delete_episode_by_id(self, id: int) -> Message:

        episode = self.get_episode_by_id(id)
        podcast = self.session.get(Podcast, episode.podcast_id)
        if self.user_login.id != podcast.author_id and self.user_login.role != UserRole.ADMIN.value:
            raise NoPermissionException()

        self._delete_existing_cover(episode)
        if episode.enclosure_path:
            delete_file_from_contents(episode.enclosure_path)

        self.session.delete(episode)
        self.session.commit()

        return Message(detail="Episode deleted.")

    def get_cover_by_id(self, id: int) -> FileResponse:

        episode = self.get_episode_by_id(id)

        if not episode.itunes_image_path:
            raise CoverNotFoundException()

        return FileResponse(episode.itunes_image_path)

    async def update_cover_by_id(self, id: int, cover_update: UploadFile) -> Message:

        episode = self.get_episode_by_id(id)
        podcast = self.session.get(Podcast, episode.podcast_id)
        if self.user_login.id != podcast.author_id and self.user_login.role != UserRole.ADMIN.value:
            raise NoPermissionException()

        self._delete_existing_cover(episode)
        episode.itunes_image_path = await save_file_to_contents(cover_update)

        self.session.add(episode)
        self.session.commit()

        return Message(detail="Cover changed.")

    def get_audio_by_id(self, id: int) -> FileResponse:

        episode = self.get_episode_by_id(id)

        if not episode.enclosure_path:
            raise AudioNotFoundException()
        return FileResponse(episode.itunes_image_path)

    async def update_audio_by_id(self, id: int, audio_update: UploadFile) -> Message:

        episode = self.get_episode_by_id(id)
        podcast = self.session.get(Podcast, episode.podcast_id)
        if self.user_login.id != podcast.author_id and self.user_login.role != UserRole.ADMIN.value:
            raise NoPermissionException()

        self._delete_existing_audio(episode)
        episode.enclosure_path = await save_file_to_contents(audio_update)

        self.session.add(episode)
        self.session.commit()

        return Message(detail="Audio changed.")

    def _delete_existing_cover(self, episode: Episode):

        if episode.itunes_image_path:
            delete_file_from_contents(episode.itunes_image_path)

    def _delete_existing_audio(self, episode: Episode):

        if episode.enclosure_path:
            delete_file_from_contents(episode.enclosure_path)
