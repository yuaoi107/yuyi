from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    # Project Configs, no need to cover

    # Basic Info
    PROJECT_TITLE: str = "Yuyi APIs"
    PROJECT_SUMMARY: str = "雨呓（Yuyi）是一个泛用型播客托管平台的 RESTful API 后端。"
    PROJECT_DESCRIPTION: str = """
作者： [Coin Chiang](mailto://myabandonment@foxmail.com)
    
仓库： [Yuyi on Gitee](https://gitee.com/coinchiang/yuyi)
"""

    GENERATOR_NAME: str = "Yuyi 0.1.0"

    # Environment Specific Configs, need to cover

    # Database
    PGDB_URL: str = ""

    # Base Url
    BASE_URL: str = "http://localhost:8000/"

    # Static files dir
    CONTENTS_DIR: str = ""

    # Authentication & Authorization
    SECRET_KEY: str = ""
    ALGORITHM: str = ""
    ACCESS_TOKEN_EXPIRE_MINUTES: int = ""

    # DevOps
    STATE_CHECK_KEY: str = ""

    class Config:
        env_file = ".env"


settings = Settings()
