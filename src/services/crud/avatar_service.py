from fastapi import HTTPException, UploadFile, status
from fastapi.responses import RedirectResponse
from sqlmodel import Session

from ...common.util import ContentFileType, archive_file, delete_by_url, Message
from ...models.user import User


class AvatarService:

    @staticmethod
    async def create_avatar(session: Session, user_id: int, avatar: UploadFile) -> Message:
        db_user = session.get(User, user_id)
        if not db_user:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found.")
        try:
            if db_user.avatar_path:
                delete_by_url(db_user.avatar_path)
            avatar_url = await archive_file(avatar, ContentFileType.AVATAR)
        except Exception:
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to save file.")
        db_user.avatar_path = avatar_url
        session.add(db_user)
        session.commit()
        return {"detail": "Avatar changed."}

    @staticmethod
    def get_avatar(session: Session, user_id: int) -> RedirectResponse:
        db_user = session.get(User, user_id)
        if not db_user:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found.")
        return RedirectResponse(db_user.avatar_path)
