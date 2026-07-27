from app.infrastructure.ocr.tesseract_service import TesseractOCRService
from app.infrastructure.email.smtp_service import SMTPEmailService
from app.domain.interfaces import OCRService, EmailService

def get_ocr_service() -> OCRService:
    return TesseractOCRService()

def get_email_service() -> EmailService:
    return SMTPEmailService()
















