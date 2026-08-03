from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field


class EmailRequest(BaseModel):
    photo_id: int = Field(description="ID загруженной фотографии", gt=0)
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


class AnalyzeDocResponse(BaseModel):
    photo_id: int
    text: str


class EmailResponse(BaseModel):
    photo_id: int
    recipient_email: EmailStr
    email_sent: bool
