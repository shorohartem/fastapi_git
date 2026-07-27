import os
import pytesseract
from PIL import Image
from app.domain.interfaces import OCRService
from app.core.config import settings


class TesseractOCRService(OCRService):

    def extract_text(self, image_path: str) -> str:

        full_path = os.path.join(settings.MEDIA_ROOT, image_path)

        if not os.path.exists(full_path):
            raise FileNotFoundError(f"Image not found: {full_path}")

        image = Image.open(full_path)
        text = pytesseract.image_to_string(image, lang=settings.TESSERACT_LANG)

        return text.strip()