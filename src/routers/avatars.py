from typing import Annotated

from fastapi import APIRouter, File, Query, UploadFile, status
from fastapi.responses import RedirectResponse

from src.common.auth import UserDep
from src.services.shared import check_permission
from ..database.database import SessionDep
from ..common.util import add_responses, Message
from ..services.avatar_service import AvatarService

router = APIRouter(
    prefix="/avatars",
    tags=["头像"]
)


@router.put(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=Message,
    summary="修改头像",
    responses=add_responses(401, 404, 500)
)
async def put_with_query(
    user_login: UserDep,
    session: SessionDep,
    user_id: Annotated[int, Query()],
    avatar: Annotated[UploadFile, File()]
):
    check_permission(user_login, user_id)
    return await AvatarService.create_avatar(session, user_id, avatar)


@router.get(
    "",
    status_code=status.HTTP_302_FOUND,
    response_class=RedirectResponse,
    summary="获取头像文件",
    responses=add_responses(404)
)
async def get_by_path(session: SessionDep, user_id: Annotated[int, Query()]):
    return AvatarService.get_avatar(session, user_id)
