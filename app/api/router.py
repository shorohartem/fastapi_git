from io import BytesIO
import smtplib

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from PIL import Image, UnidentifiedImageError
from starlette.concurrency import run_in_threadpool

from app.core.config import settings
from app.domain.models import (
    AnalyzeDocResponse,
    EmailRequest,
    EmailResponse,
    PhotoResponse,
)
from app.infrastructure.email.smtp_service import SMTPEmailService
from app.infrastructure.ocr.tesseract_service import TesseractOCRService
from app.infrastructure.storage.photo_repository import PhotoRepository

router = APIRouter(prefix="/api/v1", tags=["ocr"])

SUPPORTED_IMAGE_FORMATS = {
    "JPEG": (".jpg", "image/jpeg"),
    "PNG": (".png", "image/png"),
}


def get_photo_repository() -> PhotoRepository:
    return PhotoRepository(settings.MEDIA_ROOT)


def validate_image(contents: bytes) -> tuple[str, str]:
    try:
        with Image.open(BytesIO(contents)) as image:
            image.verify()
            image_format = image.format
    except (UnidentifiedImageError, OSError, ValueError) as exc:
        raise HTTPException(status_code=422, detail="File is not a valid image") from exc

    if image_format not in SUPPORTED_IMAGE_FORMATS:
        raise HTTPException(status_code=415, detail="Only JPEG and PNG images are supported")

    return SUPPORTED_IMAGE_FORMATS[image_format]


async def get_stored_photo(photo_id: int) -> dict:
    photo = await run_in_threadpool(get_photo_repository().get, photo_id)
    if photo is None:
        raise HTTPException(status_code=404, detail=f"Photo with ID {photo_id} not found")
    return photo


async def extract_photo_text(photo: dict) -> str:
    return await run_in_threadpool(
        TesseractOCRService().extract_text,
        photo["storage_path"],
    )


@router.post(
    "/photos",
    response_model=PhotoResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["photos"],
)
async def upload_photo(file: UploadFile = File(...)):
    contents = await file.read()
    await file.close()

    if not contents:
        raise HTTPException(status_code=422, detail="Uploaded file is empty")

    suffix, content_type = await run_in_threadpool(validate_image, contents)
    photo = await run_in_threadpool(
        get_photo_repository().create,
        contents,
        suffix,
        file.filename or "image",
        content_type,
    )
    return PhotoResponse(**photo)


@router.post("/analyze_doc", response_model=AnalyzeDocResponse)
async def analyze_doc(photo_id: int):
    photo = await get_stored_photo(photo_id)
    extracted_text = await extract_photo_text(photo)
    return AnalyzeDocResponse(photo_id=photo_id, text=extracted_text)


@router.post("/send_message_to_email", response_model=EmailResponse)
async def send_message_to_email(request: EmailRequest):
    photo = await get_stored_photo(request.photo_id)
    extracted_text = await extract_photo_text(photo)

    try:
        await run_in_threadpool(
            SMTPEmailService().send_notification,
            str(request.recipient_email),
            photo["storage_path"],
            extracted_text,
        )
    except (OSError, smtplib.SMTPException) as exc:
        raise HTTPException(status_code=502, detail="Email service unavailable") from exc

    return EmailResponse(
        photo_id=request.photo_id,
        recipient_email=request.recipient_email,
        email_sent=True,
    )
