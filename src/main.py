from typing import Annotated

from fastapi import FastAPI, HTTPException, Request, status, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from src.config.settings import settings
from src.core.constants import CommonMessage
from src.models import *
from src.core.database import create_db_and_tables
from src.core.exceptions import AppError, AuthenticationFailedError
from src.api.endpoints import auth, users, podcasts, episodes

create_db_and_tables()

app = FastAPI(
    title=settings.PROJECT_TITLE,
    summary=settings.PROJECT_SUMMARY,
    description=settings.PROJECT_DESCRIPTION
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.exception_handler(AppError)
async def app_exception_handler(request: Request, exc: AppError):
    if isinstance(exc, AuthenticationFailedError):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return JSONResponse(status_code=exc.code, content={"message": exc.message})


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(exc)
    return JSONResponse(status_code=500, content={"message": "服务器内部错误"})


@app.get("/state", status_code=status.HTTP_200_OK, include_in_schema=False)
async def check_app_state(key: Annotated[str, Query()]):
    if key != settings.STATE_CHECK_KEY:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return CommonMessage(message="Running fine.")

for router in [users.router, podcasts.router, episodes.router, auth.router]:
    app.include_router(router)
