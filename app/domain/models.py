from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field


class ImagePathRequest(BaseModel):
    image_path: str = Field(
        description="Путь к изображению относительно MEDIA_ROOT",
        examples=["photo.jpg"],
    )


class EmailRequest(BaseModel):
    image_path: str = Field(description="Путь к проанализированному изображению")
    extracted_text: str = Field(description="Распознанный текст")
    recipient_email: EmailStr = Field(description="Email получателя")


class TaskAcceptedResponse(BaseModel):
    task_id: str
    status: str = "queued"


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    result: Any | None = None
    error: str | None = None


class PhotoResponse(BaseModel):
    id: int
    original_filename: str
    content_type: str
    created_at: datetime
