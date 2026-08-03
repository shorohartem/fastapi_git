from app.infrastructure.email.smtp_service import SMTPEmailService
from app.infrastructure.ocr.tesseract_service import TesseractOCRService

from .celery_app import celery_app


@celery_app.task(name="analyze_document")
def analyze_document(image_path: str) -> dict[str, str]:
    text = TesseractOCRService().extract_text(image_path)
    return {"text": text, "image_path": image_path, "status": "completed"}


@celery_app.task(name="send_email_notification")
def send_email_notification(
    recipient_email: str,
    image_path: str,
    extracted_text: str,
) -> dict[str, str]:
    SMTPEmailService().send_notification(recipient_email, image_path, extracted_text)
    return {"recipient_email": recipient_email, "status": "sent"}
