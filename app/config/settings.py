from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    PROJECT_TITLE: str = ""
    PROJECT_SUMMARY: str = ""
    PGDB_URL: str = ""
    STATE_CHECK_KEY: str = ""
    ARCHIVES_DIR: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
