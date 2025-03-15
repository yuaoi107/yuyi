from time import time
from email.utils import formatdate
from typing import Annotated, BinaryIO
from uuid import uuid4

from fastapi import Depends, UploadFile
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select

from src.core.auth import UserDep
from src.core.database import SessionDep
from src.services.cos_service import CosService, CosServiceDep
from src.core.constants import UserRole, CommonMessage
from src.models.episode import Episode, EpisodeCreate, EpisodeUpdate
from src.models.podcast import Podcast
from src.models.user import User
from src.services.rss_service import RssService, RssServiceDep
from src.services.utils import delete_file_from_contents
from src.core.exceptions import (
    EpisodeAudioNotFoundError,
    EpisodeNotFoundError,
    NoPermissionError,
    PodcastNotFoundError,
    EpisodeTitleAlreadyExistsError,
    EpisodeCoverNotFoundError
)
from src.utils.file_utils import get_audio_duration_from_binaryio, get_unique_filename


class EpisodeService:

    def __init__(self, session: Session, cos_service: CosService, rss_service: RssService, user_login: User | None = None):
        self.session = session
        self.cos_service = cos_service
        self.rss_service = rss_service
        self.user_login = user_login

    def get_episode_by_id(self, id: int) -> Episode:
        episode = self.session.get(Episode, id)
        if not episode:
            raise EpisodeNotFoundError()
        return episode

    def get_all_episodes(self, offset: int, limit: int) -> list[Episode]:
        return self.session.exec(select(Episode).offset(offset).limit(limit)).all()

    def get_episodes_by_podcast_id(self, podcast_id: int, offset: int, limit: int) -> list[Episode]:
        podcast = self.session.get(Podcast, podcast_id)
        if not podcast:
            raise PodcastNotFoundError()

        return self.session.exec(select(Episode).where(Episode.podcast_id == podcast_id).offset(offset).limit(limit)).all()

    def create_episode_by_podcast_id(self, podcast_id: int, episode_upload: EpisodeCreate) -> Episode:
        podcast = self.session.get(Podcast, podcast_id)
        if not podcast:
            raise PodcastNotFoundError()
        if self.user_login.id != podcast.author_id and self.user_login.role != UserRole.ADMIN.value:
            raise NoPermissionError()

        same_title_episode = self.session.exec(select(Episode).where(
            Episode.podcast_id == podcast_id, Episode.title == episode_upload.title)).first()

        if same_title_episode:
            raise EpisodeTitleAlreadyExistsError()

        extra_data = {
            "podcast_id": podcast_id,
            "guid": uuid4().hex,
            "pub_date": formatdate(time(), True)
        }

        new_episode = Episode.model_validate(episode_upload, update=extra_data)
        self.session.add(new_episode)
        self.session.commit()

        self.session.refresh(podcast)
        self.rss_service.update_podcast_rss(podcast)
        self.session.add(podcast)
        self.session.commit()

        self.session.refresh(new_episode)

        return new_episode

    def update_episode_by_id(self, id: int, episode_upload: EpisodeUpdate) -> Episode:
        episode = self.get_episode_by_id(id)
        podcast = self.session.get(Podcast, episode.podcast_id)
        if self.user_login.id != podcast.author_id and self.user_login.role != UserRole.ADMIN.value:
            raise NoPermissionError()

        same_title_episode = self.session.exec(select(Episode).where(
            Episode.podcast_id == episode.podcast_id, Episode.title == episode_upload.title)).first()

        if same_title_episode:
            raise EpisodeTitleAlreadyExistsError()

        episode.sqlmodel_update(
            episode_upload.model_dump(exclude_unset=True)
        )
        self.session.add(episode)
        self.session.commit()

        self.session.refresh(podcast)
        self.rss_service.update_podcast_rss(podcast)
        self.session.add(podcast)
        self.session.commit()

        return episode

    def delete_episode_by_id(self, id: int) -> CommonMessage:
        episode = self.get_episode_by_id(id)
        podcast = self.session.get(Podcast, episode.podcast_id)
        if self.user_login.id != podcast.author_id and self.user_login.role != UserRole.ADMIN.value:
            raise NoPermissionError()

        self._delete_existing_cover(episode)
        if episode.enclosure_path:
            delete_file_from_contents(episode.enclosure_path)

        self.session.delete(episode)
        self.session.commit()

        self.session.refresh(podcast)
        self.rss_service.update_podcast_rss(podcast)
        self.session.add(podcast)
        self.session.commit()

        return CommonMessage(message="Episode Deleted.")

    def get_cover_by_id(self, id: int) -> StreamingResponse:
        episode = self.get_episode_by_id(id)

        if not episode.itunes_image_path:
            raise EpisodeCoverNotFoundError()

        return StreamingResponse(self.cos_service.fetch_file(episode.itunes_image_path))

    def update_cover_by_id(self, id: int, cover_update: UploadFile) -> CommonMessage:
        episode = self.get_episode_by_id(id)
        podcast = self.session.get(Podcast, episode.podcast_id)
        if self.user_login.id != podcast.author_id and self.user_login.role != UserRole.ADMIN.value:
            raise NoPermissionError()

        self._delete_existing_cover(episode)
        cover_filename = self._get_cover_filename(
            podcast.author.id, podcast.id, episode.id, cover_update.filename)
        self.cos_service.save_file(cover_update.file, cover_filename)
        episode.itunes_image_path = cover_filename

        self.session.add(episode)
        self.session.commit()

        self.session.refresh(podcast)
        self.rss_service.update_podcast_rss(podcast)
        self.session.add(podcast)
        self.session.commit()

        return CommonMessage(message="Cover Changed.")

    def get_audio_by_id(self, id: int) -> StreamingResponse:
        episode = self.get_episode_by_id(id)

        if not episode.enclosure_path:
            raise EpisodeAudioNotFoundError()
        return StreamingResponse(self.cos_service.fetch_file(episode.enclosure_path))

    def update_audio_by_id(self, id: int, audio_update: UploadFile) -> CommonMessage:
        episode = self.get_episode_by_id(id)
        podcast = self.session.get(Podcast, episode.podcast_id)
        if self.user_login.id != podcast.author_id and self.user_login.role != UserRole.ADMIN.value:
            raise NoPermissionError()

        self._delete_existing_audio(episode)
        episode.enclosure_length = audio_update.size
        episode.enclosure_type = audio_update.content_type

        enclosure_filename = self._get_enclosure_filename(
            podcast.author.id, podcast.id, episode.id, audio_update.filename)
        self.cos_service.save_file(audio_update.file, enclosure_filename)
        episode.enclosure_path = enclosure_filename
        episode.itunes_duration = get_audio_duration_from_binaryio(
            audio_update.file)

        self.session.add(episode)
        self.session.commit()

        self.session.refresh(podcast)
        self.rss_service.update_podcast_rss(podcast)
        self.session.add(podcast)
        self.session.commit()

        return CommonMessage(message="Audio Changed.")

    def _get_cover_filename(self, author_id, podcast_id, episode_id, original_filename: str) -> str:

        return f"users/{author_id}/podcasts/{podcast_id}/episodes/{episode_id}/cover/{get_unique_filename(original_filename)}"

    def _get_enclosure_filename(self, author_id, podcast_id, episode_id, original_filename: str) -> str:

        return f"users/{author_id}/podcasts/{podcast_id}/episodes/{episode_id}/enclosure/{get_unique_filename(original_filename)}"

    def _delete_existing_cover(self, episode: Episode):
        if episode.itunes_image_path:
            self.cos_service.delete_file(episode.itunes_image_path)

    def _delete_existing_audio(self, episode: Episode):
        if episode.enclosure_path:
            self.cos_service.delete_file(episode.enclosure_path)


def get_episode_service(session: SessionDep, cos_service: CosServiceDep, rss_service: RssServiceDep):
    return EpisodeService(session, cos_service, rss_service)


def get_episode_service_with_login(session: SessionDep, cos_service: CosServiceDep, rss_service: RssServiceDep, user_login: UserDep):
    return EpisodeService(session, cos_service, rss_service, user_login)


EpisodeServiceDep = Annotated[EpisodeService, Depends(get_episode_service)]

EpisodeServiceLoginDep = Annotated[EpisodeService,
                                   Depends(get_episode_service_with_login)]
