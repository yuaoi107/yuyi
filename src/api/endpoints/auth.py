from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.core.auth import Token
from src.core.database import SessionDep
from src.services.auth_service import AuthenticationService

router = APIRouter(tags=["认证"])


@router.post("/token", response_model=Token, summary="获取登陆 token")
async def post_token(session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    auth_service = AuthenticationService(session, form_data)
    return auth_service.get_token()
