from time import time
from email.utils import formatdate
from uuid import uuid4

from fastapi import UploadFile
from fastapi.responses import FileResponse
from sqlmodel import Session, select

from src.core.constants import ContentFileType, UserRole, CommonMessage
from src.models.episode import Episode, EpisodeCreate, EpisodeUpdate
from src.models.podcast import Podcast
from src.models.user import User
from src.services.rss_service import RSSService
from src.services.utils import save_file_to_contents, delete_file_from_contents
from src.core.exceptions import (
    EpisodeAudioNotFoundException,
    EpisodeNotFoundException,
    NoPermissionException,
    PodcastNotFoundException,
    EpisodeTitleAlreadyExistsException,
    EpisodeCoverNotFoundException
)


class EpisodeService:

    def __init__(self, session: Session, user_login: User | None = None):
        self.session = session
        self.user_login = user_login
        self.rss_service = RSSService()

    def get_episode_by_id(self, id: int) -> Episode:
        episode = self.session.get(Episode, id)
        if not episode:
            raise EpisodeNotFoundException()
        return episode

    def get_all_episodes(self, offset: int, limit: int) -> list[Episode]:
        return self.session.exec(select(Episode).offset(offset).limit(limit)).all()

    def get_episodes_by_podcast_id(self, podcast_id: int, offset: int, limit: int) -> list[Episode]:
        podcast = self.session.get(Podcast, podcast_id)
        if not podcast:
            raise PodcastNotFoundException()

        return self.session.exec(select(Episode).where(Episode.podcast_id == podcast_id).offset(offset).limit(limit)).all()

    def create_episode_by_podcast_id(self, podcast_id: int, episode_upload: EpisodeCreate) -> Episode:
        podcast = self.session.get(Podcast, podcast_id)
        if not podcast:
            raise PodcastNotFoundException()
        if self.user_login.id != podcast.author_id and self.user_login.role != UserRole.ADMIN.value:
            raise NoPermissionException()

        same_title_episode = self.session.exec(select(Episode).where(
            Episode.podcast_id == podcast_id, Episode.title == episode_upload.title)).first()

        if same_title_episode:
            raise EpisodeTitleAlreadyExistsException()

        extra_data = {
            "podcast_id": podcast_id,
            "guid": uuid4().hex,
            "pub_date": formatdate(time(), True)
        }

        new_episode = Episode.model_validate(episode_upload, update=extra_data)
        self.session.add(new_episode)
        self.session.commit()

        self.rss_service.update_podcast_rss(podcast)
        self.session.add(podcast)
        self.session.commit()

        self.session.refresh(new_episode)

        return new_episode

    def update_episode_by_id(self, id: int, episode_upload: EpisodeUpdate) -> Episode:
        episode = self.get_episode_by_id(id)
        podcast = self.session.get(Podcast, episode.podcast_id)
        if self.user_login.id != podcast.author_id and self.user_login.role != UserRole.ADMIN.value:
            raise NoPermissionException()

        same_title_episode = self.session.exec(select(Episode).where(
            Episode.podcast_id == episode.podcast_id, Episode.title == episode_upload.title)).first()

        if same_title_episode:
            raise EpisodeTitleAlreadyExistsException()

        episode.sqlmodel_update(
            episode_upload.model_dump(exclude_unset=True)
        )
        self.session.add(episode)
        self.session.commit()
        self.session.refresh(episode)

        self.rss_service.update_podcast_rss(podcast)
        self.session.add(podcast)
        self.session.commit()

        return episode

    def delete_episode_by_id(self, id: int) -> CommonMessage:
        episode = self.get_episode_by_id(id)
        podcast = self.session.get(Podcast, episode.podcast_id)
        if self.user_login.id != podcast.author_id and self.user_login.role != UserRole.ADMIN.value:
            raise NoPermissionException()

        self._delete_existing_cover(episode)
        if episode.enclosure_path:
            delete_file_from_contents(episode.enclosure_path)

        self.session.delete(episode)
        self.session.commit()

        self.rss_service.update_podcast_rss(podcast)
        self.session.add(podcast)
        self.session.commit()

        return CommonMessage(message="Episode Deleted.")

    def get_cover_by_id(self, id: int) -> FileResponse:
        episode = self.get_episode_by_id(id)

        if not episode.itunes_image_path:
            raise EpisodeCoverNotFoundException()

        return FileResponse(episode.itunes_image_path)

    async def update_cover_by_id(self, id: int, cover_update: UploadFile) -> CommonMessage:
        episode = self.get_episode_by_id(id)
        podcast = self.session.get(Podcast, episode.podcast_id)
        if self.user_login.id != podcast.author_id and self.user_login.role != UserRole.ADMIN.value:
            raise NoPermissionException()

        self._delete_existing_cover(episode)
        episode.itunes_image_path = await save_file_to_contents(cover_update, ContentFileType.EPISODE_COVER)

        self.session.add(episode)
        self.session.commit()

        return CommonMessage(message="Cover Changed.")

    def get_audio_by_id(self, id: int) -> FileResponse:
        episode = self.get_episode_by_id(id)

        if not episode.enclosure_path:
            raise EpisodeAudioNotFoundException()
        return FileResponse(episode.enclosure_path)

    async def update_audio_by_id(self, id: int, audio_update: UploadFile) -> CommonMessage:
        episode = self.get_episode_by_id(id)
        podcast = self.session.get(Podcast, episode.podcast_id)
        if self.user_login.id != podcast.author_id and self.user_login.role != UserRole.ADMIN.value:
            raise NoPermissionException()

        self._delete_existing_audio(episode)
        episode.enclosure_length = audio_update.size
        episode.enclosure_type = audio_update.content_type
        episode.enclosure_path = await save_file_to_contents(audio_update, ContentFileType.AUDIO)

        self.session.add(episode)
        self.session.commit()

        self.session.refresh(episode)
        self.rss_service.update_podcast_rss(podcast)
        self.session.add(podcast)
        self.session.commit()

        return CommonMessage(message="Audio Changed.")

    def _delete_existing_cover(self, episode: Episode):
        if episode.itunes_image_path:
            delete_file_from_contents(episode.itunes_image_path)

    def _delete_existing_audio(self, episode: Episode):
        if episode.enclosure_path:
            delete_file_from_contents(episode.enclosure_path)
