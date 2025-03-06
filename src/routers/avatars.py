from typing import Annotated

from fastapi import APIRouter, File, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse, RedirectResponse

from ..database.database import SessionDep
from ..utils.util import FileType, archive_file, delete_by_url, add_responses, Message
from ..models.user import User

router = APIRouter(
    prefix="/avatars",
    tags=["头像"]
)


@router.put("", status_code=status.HTTP_201_CREATED, response_model=Message, summary="修改头像",
            responses=add_responses(404, 500))
async def create_avatar(session: SessionDep, user_id: Annotated[int, Query()], avatar: Annotated[UploadFile, File()]):

    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found.")
    try:
        if db_user.avatar_url:
            delete_by_url(db_user.avatar_url)
        avatar_url = await archive_file(avatar, FileType.AVATAR)
    except Exception:
        raise HTTPException(
            status.HTTP_500_INTERNAL_SERVER_ERROR, "Failed to save file.")
    db_user.avatar_url = avatar_url
    session.add(db_user)
    session.commit()
    return {"detail": "Avatar changed."}


@router.get("", status_code=status.HTTP_302_FOUND, response_class=RedirectResponse, summary="获取头像文件",
            responses=add_responses(404))
async def get_avatar(session: SessionDep, user_id: Annotated[int, Query()]):
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found.")
    return RedirectResponse(db_user.avatar_url)
