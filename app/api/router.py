from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from app.domain.models import ImagePathRequest, AnalyzeResponse, EmailRequest, EmailResponse
from app.domain.interfaces import OCRService, EmailService
from app.api.dependencies import get_ocr_service, get_email_service
from app.infrastructure.tasks.ocr_tasks import analyze_and_notify
import httpx

router = APIRouter(prefix="/api/v1", tags=["ocr"])


@router.get("/health")
async def health_check():
    return {"status": "ДИМА СУКА"}


@router.post("/analyze_doc", response_model=AnalyzeResponse, status_code=200)
async def analyze_doc(
    request: ImagePathRequest,
    background_tasks: BackgroundTasks,
    ocr_service: OCRService = Depends(get_ocr_service),
):
    try:
        text = ocr_service.extract_text(request.image_path)

        if request.email:
            analyze_and_notify.delay(request.image_path, request.email)

        return AnalyzeResponse(text=text)

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"OCR error: {str(e)}")


@router.post("/send_message_to_email", response_model=EmailResponse, status_code=200)
async def send_message_to_email(
    request: EmailRequest,
    email_service: EmailService = Depends(get_email_service),
):
    try:
        success = email_service.send_notification(
            recipient=request.recipient_email,
            image_path=request.image_path,
            extracted_text=request.extracted_text
        )

        if not success:
            raise HTTPException(status_code=422, detail="Failed to send email")

        return EmailResponse(message="Email sent successfully")

    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Email error: {str(e)}")


@router.post("/analyze_doc_by_id", response_model=AnalyzeResponse, status_code=200)
async def analyze_doc_by_id(
    photo_id: int,
    email: str = None,
    ocr_service: OCRService = Depends(get_ocr_service),
):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://host.docker.internal:8000/api/photo/{photo_id}/path/")
            if response.status_code != 200:
                raise HTTPException(status_code=404, detail=f"Photo with ID {photo_id} not found in Django")
            image_path = response.json().get('path')
            if not image_path:
                raise HTTPException(status_code=404, detail="Photo path not found")
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="Django service unavailable")

    try:
        text = ocr_service.extract_text(image_path)

        if email:
            analyze_and_notify.delay(image_path, email)

        return AnalyzeResponse(text=text)

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Image file not found: {image_path}")
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"OCR error: {str(e)}")