from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    MEDIA_ROOT: str = "/shared_media"

    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"

    DJANGO_BASE_URL: str = "http://django:8000"
    DJANGO_MEDIA_URL: str = ""

    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    NOTIFICATION_EMAIL: str = ""
    # MailHog does not use TLS. Set this to true only for a real SMTP provider.
    SMTP_USE_TLS: bool = False

    TESSERACT_LANG: str = "rus+eng"


settings = Settings()
