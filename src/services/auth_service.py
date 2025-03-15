from datetime import timedelta
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session

from src.config.settings import settings
from src.core.auth import Token, authenticate_user, create_access_token
from src.core.exceptions import AuthenticationFailedError


class AuthenticationService:

    def __init__(self, session: Session, form_data: OAuth2PasswordRequestForm):
        self.session = session
        self.form_data = form_data

    def get_token(self) -> Token:
        user = authenticate_user(
            self.session, self.form_data.username, self.form_data.password)
        if not user:
            raise AuthenticationFailedError()
        access_token_expires = timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username},
            expires_delta=access_token_expires
        )
        return Token(access_token=access_token, token_type="bearer")
