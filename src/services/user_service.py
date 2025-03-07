from datetime import date

from fastapi import HTTPException, status
from sqlmodel import Session, select

from ..common.util import Message
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
        db_user = User.model_validate(user, update=extra_data)

        session.add(db_user)
        session.commit()
        session.refresh(db_user)

        return db_user

    @staticmethod
    def get_users(session: Session, offset: int, limit: int) -> list[User]:
        users = session.exec(select(User).offset(offset).limit(limit)).all()
        return users

    @staticmethod
    def get_user(session: Session, id: int) -> User:
        db_user = session.get(User, id)
        if not db_user:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found.")
        return db_user

    @staticmethod
    def update_user(session: Session, id: int, user: UserUpdate) -> User:
        db_user = session.get(User, id)

        if not db_user:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found.")

        if session.exec(select(User).where(User.nickname == user.nickname)).first():
            raise HTTPException(status.HTTP_409_CONFLICT, "Nickname taken.")

        user_data = user.model_dump(exclude_unset=True)
        extra_data = {}

        if "password" in user_data:
            hashed_password = hash_password(user_data["password"])
            extra_data["hashed_password"] = hashed_password

        db_user.sqlmodel_update(user_data, update=extra_data)
        session.add(db_user)
        session.commit()
        session.refresh(db_user)

        return db_user

    @staticmethod
    def delete_user(session: Session, id: int) -> Message:
        user = session.get(User, id)
        if not user:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found.")
        session.delete(user)
        session.commit()
        return {"detail": "Successfully deleted"}

    # @staticmethod
    # def get_me(user: User) -> User:
    #     return user
