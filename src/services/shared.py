from fastapi import HTTPException

from src.common.util import UserRole
from src.models.user import User


def check_permission(user_login: User) -> None:
    if user_login.role != UserRole.ADMIN and user_login.id != id:
        raise HTTPException(403)
