from datetime import date

from fastapi import UploadFile
from fastapi.responses import FileResponse
from sqlmodel import Session, select

from src.models.episode import Episode
from src.models.podcast import Podcast
from src.core.constants import ContentFileType, UserRole
from src.core.constants import Message
from src.services.util import save_file_to_contents, delete_file_from_contents
from src.core.auth import hash_password
from src.core.exceptions import (
    UserAlreadyExistsException,
    NameAlreadyExistsException,
    UserNotFoundException,
    AvatarNotFoundException,
    NoPermissionException
)
from src.models.user import (
    User,
    UserCreate,
    UserUpdate
)


class UserService:

    def __init__(self, session: Session, user_login: User | None = None):
        self.session = session
        self.user_login = user_login

    def create_user(self, user: UserCreate) -> User:

        existing_user = self.session.exec(
            select(User).where(User.username == user.username)
        ).first()
        if existing_user:
            raise UserAlreadyExistsException()

        same_name_user = self.session.exec(
            select(User).where(User.nickname == user.nickname)
        ).first()
        if same_name_user:
            raise NameAlreadyExistsException()

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
            raise UserNotFoundException()

        return user

    def update_user_by_id(self, user_id: int, user_update: UserUpdate) -> User:

        if self.user_login.id != user_id and self.user_login.role != UserRole.ADMIN.value:
            raise NoPermissionException()

        user = self.get_user_by_id(user_id)

        same_name_user = self.session.exec(
            select(User).where(User.nickname == user_update.nickname)
        ).first()
        if same_name_user:
            raise NameAlreadyExistsException()

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

    def delete_user_by_id(self, user_id: int) -> Message:

        if self.user_login.id != user_id and self.user_login.role != UserRole.ADMIN.value:
            raise NoPermissionException()

        user = self.get_user_by_id(user_id)
        self._delete_existing_avatar(user)

        for podcast in user.podcasts:
            self._delete_podcast(user)

        self.session.delete(user)
        self.session.commit()

        return Message(detail="Successfully deleted")

    def get_avatar_by_id(self, user_id: int) -> FileResponse:

        user = self.get_user_by_id(user_id)
        if not user.avatar_path:
            raise AvatarNotFoundException()

        return FileResponse(user.avatar_path)

    async def update_avatar_by_id(self, user_id: int, avatar_update: UploadFile) -> Message:

        if self.user_login.id != user_id and self.user_login.role != UserRole.ADMIN.value:
            raise NoPermissionException()

        user = self.get_user_by_id(user_id)

        self._delete_existing_avatar(user)
        user.avatar_path = await save_file_to_contents(avatar_update, ContentFileType.AVATAR)

        self.session.add(user)
        self.session.commit()

        return Message(detail="Avatar changed.")

    def _delete_existing_avatar(self, user: User) -> None:

        if user.avatar_path:
            delete_file_from_contents(user.avatar_path)

    def _delete_podcast(self, podcast: Podcast):

        if podcast.itunes_image_path:
            delete_file_from_contents(podcast.itunes_image_path)
        if podcast.feed_path:
            delete_file_from_contents(podcast.feed_path)

        for episode in podcast.episodes:
            self._delete_episode(episode)

        self.session.delete(podcast)

    def _delete_episode(self, episode: Episode):

        if episode.itunes_image_path:
            delete_file_from_contents(episode.itunes_image_path)
        if episode.enclosure_path:
            delete_file_from_contents(episode.enclosure_path)

        self.session.delete(episode)
