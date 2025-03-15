from datetime import date
from typing import Annotated

from fastapi import Depends, UploadFile
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select

from src.core.database import SessionDep
from src.services.cos_service import CosService, CosServiceDep
from src.models.episode import Episode
from src.models.podcast import Podcast
from src.models.user import User, UserCreate, UserUpdate
from src.core.auth import UserDep, hash_password
from src.core.constants import UserRole, CommonMessage
from src.core.exceptions import (
    UserAlreadyExistsError,
    UserNameAlreadyExistsError,
    UserNotFoundError,
    UserAvatarNotFoundError,
    NoPermissionError
)
from src.utils.file_utils import get_unique_filename


class UserService:

    def __init__(self, session: Session, cos_service: CosService, user_login: User | None = None):

        self.session = session
        self.user_login = user_login
        self.cos_service = cos_service

    def create_user(self, user: UserCreate) -> User:

        existing_user = self.session.exec(
            select(User).where(User.username == user.username)
        ).first()
        if existing_user:
            raise UserAlreadyExistsError()

        same_name_user = self.session.exec(
            select(User).where(User.nickname == user.nickname)
        ).first()
        if same_name_user:
            raise UserNameAlreadyExistsError()

        hashed_password = hash_password(user.password)
        extra_data = {
            "hashed_password": hashed_password,
            "createtime": date.today().isoformat()
        }

        new_user = User.model_validate(user, update=extra_data)

        self.session.add(new_user)
        self.session.commit()
        self.session.refresh(new_user)

        return new_user

    def get_all_users(self, offset: int, limit: int) -> list[User]:

        return self.session.exec(
            select(User).offset(offset).limit(limit)
        ).all()

    def get_user_by_id(self, user_id: int) -> User:

        user = self.session.get(User, user_id)
        if not user:
            raise UserNotFoundError()

        return user

    def update_user_by_id(self, user_id: int, user_update: UserUpdate) -> User:

        self._check_permission(user_id)
        user = self.get_user_by_id(user_id)

        same_name_user = self.session.exec(
            select(User).where(User.nickname == user_update.nickname)
        ).first()
        if same_name_user:
            raise UserNameAlreadyExistsError()

        user_data = user_update.model_dump(exclude_unset=True)
        extra_data = {}

        if "password" in user_data:
            hashed_password = hash_password(user_data["password"])
            extra_data["hashed_password"] = hashed_password

        user.sqlmodel_update(user_data, update=extra_data)
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)

        return user

    def delete_user_by_id(self, user_id: int) -> CommonMessage:

        self._check_permission(user_id)

        user = self.get_user_by_id(user_id)
        self._delete_existing_avatar(user)

        for podcast in user.podcasts:
            self._delete_podcast(podcast)

        self.session.delete(user)
        self.session.commit()

        return CommonMessage(message="Successfully Deleted.")

    def get_avatar_by_id(self, user_id: int) -> StreamingResponse:

        user = self.get_user_by_id(user_id)

        if not user.avatar_path:
            raise UserAvatarNotFoundError()

        return StreamingResponse(self.cos_service.fetch_file(user.avatar_path))

    def update_avatar_by_id(self, user_id: int, avatar_update: UploadFile) -> CommonMessage:

        self._check_permission(user_id)

        user = self.get_user_by_id(user_id)

        self._delete_existing_avatar(user)

        avatar_filename = self._get_avatar_filename(
            user.id, avatar_update.filename)
        self.cos_service.save_file(avatar_update.file, avatar_filename)
        user.avatar_path = avatar_filename

        self.session.add(user)
        self.session.commit()

        return CommonMessage(message="Avatar Changed.")

    def _get_avatar_filename(self, user_id: int, original_filename: str) -> str:

        return f"users/{user_id}/avatar/{get_unique_filename(original_filename)}"

    def _delete_existing_avatar(self, user: User) -> None:

        if user.avatar_path:
            self.cos_service.delete_file(user.avatar_path)

    def _delete_podcast(self, podcast: Podcast):

        if podcast.itunes_image_path:
            self.cos_service.delete_file(podcast.itunes_image_path)
        if podcast.feed_path:
            self.cos_service.delete_file(podcast.feed_path)

        for episode in podcast.episodes:
            self._delete_episode(episode)

        self.session.delete(podcast)

    def _delete_episode(self, episode: Episode):

        if episode.itunes_image_path:
            self.cos_service.delete_file(episode.itunes_image_path)
        if episode.enclosure_path:
            self.cos_service.delete_file(episode.enclosure_path)

        self.session.delete(episode)

    def _check_permission(self, user_id: int):

        if self.user_login.id != user_id and \
                self.user_login.role != UserRole.ADMIN.value:
            raise NoPermissionError()


def get_user_service(session: SessionDep, cos_service: CosServiceDep):
    return UserService(session, cos_service)


def get_user_service_with_login(session: SessionDep, cos_service: CosServiceDep, user_login: UserDep):
    return UserService(session, cos_service, user_login)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]

UserServiceLoginDep = Annotated[UserService,
                                Depends(get_user_service_with_login)]
