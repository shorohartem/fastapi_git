from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):

    MEDIA_ROOT: str = "/shared_media"

    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"

    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    NOTIFICATION_EMAIL: str = ""

    TESSERACT_LANG: str = "rus+eng"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()