from .celery_app import celery_app
from app.infrastructure.email.smtp_service import SMTPEmailService
from app.infrastructure.ocr.tesseract_service import TesseractOCRService


@celery_app.task(name="analyze_and_notify")
def analyze_and_notify(image_path: str, recipient_email: str) -> dict:

    ocr_service = TesseractOCRService()
    text = ocr_service.extract_text(image_path)

    email_service = SMTPEmailService()
    email_service.send_notification(recipient_email, image_path, text)

    return {"text": text, "status": "completed"}