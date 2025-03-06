from fastapi import HTTPException

from src.common.util import UserRole
from src.models.user import User


def permission_check(user_login: User, id):
    if user_login.role != UserRole.ADMIN and user_login.id != id:
        raise HTTPException(403)
