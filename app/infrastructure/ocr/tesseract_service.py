from io import BytesIO
from pathlib import Path

import httpx
import pytesseract
from PIL import Image

from app.core.config import settings
from app.domain.interfaces import OCRService


class TesseractOCRService(OCRService):
    def extract_text(self, image_path: str) -> str:
        image = self._open_image(image_path)
        try:
            return pytesseract.image_to_string(
                image,
                lang=settings.TESSERACT_LANG,
            ).strip()
        finally:
            image.close()

    def _open_image(self, image_path: str) -> Image.Image:
        media_root = Path(settings.MEDIA_ROOT).resolve()
        local_path = (media_root / image_path).resolve()

        if local_path.is_relative_to(media_root) and local_path.is_file():
            return Image.open(local_path)

        if settings.DJANGO_MEDIA_URL:
            image_url = (
                f"{settings.DJANGO_MEDIA_URL.rstrip('/')}/"
                f"{image_path.lstrip('/')}"
            )
            response = httpx.get(image_url, timeout=30, follow_redirects=True)
            response.raise_for_status()
            return Image.open(BytesIO(response.content))

        raise FileNotFoundError(f"Image not found: {image_path}")
