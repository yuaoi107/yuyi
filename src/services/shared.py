from fastapi import HTTPException, status

from src.common.util import UserRole
from src.models.user import User


def check_permission(user_login: User) -> None:
    if user_login.role != UserRole.ADMIN and user_login.id != id:
        raise HTTPException(403)


def get_target_user_id(user_login: User, user_id: int | None) -> int:
    if user_id is None:
        return user_login.id
    if user_login.role != UserRole.ADMIN and user_login.id != user_id:
        raise HTTPException(403)
    return user_id
