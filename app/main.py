from typing import Annotated

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.staticfiles import StaticFiles

from .models import *
from .database.database import create_db_and_tables
from .config.settings import settings
from .routers import users

create_db_and_tables()

app = FastAPI(
    title=settings.PROJECT_TITLE,
    summary=settings.PROJECT_SUMMARY,
)


@app.get("/state", status_code=status.HTTP_200_OK, include_in_schema=False)
async def check_app_state(key: Annotated[str, Query()]):
    if key != settings.STATE_CHECK_KEY:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return {"state": "fine"}

app.mount("/archives", StaticFiles(directory=settings.ARCHIVES_DIR),
          name="archives")

app.include_router(users.router)
