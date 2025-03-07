from datetime import date

from fastapi import HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlmodel import Session, select

from src.common.constants import ContentFileType

from ..common.util import Message, save_file_to_contents, delete_file_from_contents
from ..common.auth import hash_password
from ..models.user import (
    User,
    UserUpload,
    UserUpdate
)


class UserService:
    @staticmethod
    def create_user(session: Session, user: UserUpload) -> User:
        if session.exec(select(User).where(User.username == user.username)).first():
            raise HTTPException(status.HTTP_409_CONFLICT, "Username taken.")

        if session.exec(select(User).where(User.nickname == user.nickname)).first():
            raise HTTPException(status.HTTP_409_CONFLICT, "Nickname taken.")

        hashed_password = hash_password(user.password)
        extra_data = {
            "hashed_password": hashed_password,
            "createtime": date.today().isoformat()
        }
        user_db = User.model_validate(user, update=extra_data)

        session.add(user_db)
        session.commit()
        session.refresh(user_db)

        return user_db

    @staticmethod
    def get_users(session: Session, offset: int, limit: int) -> list[User]:
        users = session.exec(select(User).offset(offset).limit(limit)).all()
        return users

    @staticmethod
    def get_user(session: Session, user_id: int) -> User:
        user_db = session.get(User, user_id)
        if not user_db:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found.")
        return user_db

    @staticmethod
    def update_user(session: Session, user_id: int, user_update: UserUpdate) -> User:
        user_db = UserService.get_user(session, user_id)

        if session.exec(select(User).where(User.nickname == user_update.nickname)).first():
            raise HTTPException(status.HTTP_409_CONFLICT, "Nickname taken.")

        user_data = user_update.model_dump(exclude_unset=True)
        extra_data = {}

        if "password" in user_data:
            hashed_password = hash_password(user_data["password"])
            extra_data["hashed_password"] = hashed_password

        user_db.sqlmodel_update(user_data, update=extra_data)
        session.add(user_db)
        session.commit()
        session.refresh(user_db)

        return user_db

    @staticmethod
    def delete_user(session: Session, user_id: int) -> Message:
        user_db = UserService.get_user(session, user_id)
        session.delete(user_db)
        session.commit()
        return Message(detail="Successfully deleted")

    @staticmethod
    def get_user_avatar(session: Session, user_id: int) -> FileResponse:
        user_db = UserService.get_user(session, user_id)
        if not user_db.avatar_path:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Avatar not found.")
        return FileResponse(user_db.avatar_path)

    @staticmethod
    async def update_user_avatar(session: Session, user_id: int, avatar_update: UploadFile) -> Message:
        user_db = UserService.get_user(session, user_id)
        if user_db.avatar_path:
            delete_file_from_contents(user_db.avatar_path)
        user_db.avatar_path = await save_file_to_contents(
            avatar_update, ContentFileType.AVATAR)

        session.add(user_db)
        session.commit()

        return Message(detail="Avatar changed.")
