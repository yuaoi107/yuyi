from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    # Project info
    PROJECT_TITLE: str = ""
    PROJECT_SUMMARY: str = ""
    BASE_URL: str = ""

    # Database
    PGDB_URL: str = ""

    # Static files dir
    ARCHIVES_DIR: str = ""
    ARCHIVE_ENDPOINT: str = ""

    # Authentication & Authorization
    SECRET_KEY: str = ""
    ALGORITHM: str = ""
    ACCESS_TOKEN_EXPIRE_MINUTES: int = ""

    # DevOps
    STATE_CHECK_KEY: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
