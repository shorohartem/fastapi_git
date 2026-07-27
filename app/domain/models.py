from pydantic import BaseModel, Field
from typing import Optional


class ImagePathRequest(BaseModel):
    image_path: str = Field(
        description="Путь к изображению относительно MEDIA_ROOT",
        example="photos/cat.jpg"
    )
    email: Optional[str] = Field(
        None,
        description="Email для отправки результата",
        example="admin@example.com"
    )

class AnalyzeResponse(BaseModel):
    text: str = Field(..., description=" текст с изображения")
    status: str = Field(default="success", description="Статус операции")



class EmailRequest(BaseModel):
    image_path: str = Field(
        ...,
        description="Путь к изображению",
        example="photos/cat.jpg"
    )
    extracted_text: str = Field(
        ...,
        description="Распознанный текст для отправки",
        example="Hello world from image"
    )
    recipient_email: str = Field(
        ...,
        description="Email получателя",
        example="admin@example.com"
    )

class EmailResponse(BaseModel):
    message: str = Field(..., description="Сообщение о результате")
    status: str = Field(default="sent", description="Статус операции")



class HealthResponse(BaseModel):
    status: str = Field(default="ok", description="Статус сервиса")