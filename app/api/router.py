import httpx
from celery.result import AsyncResult
from fastapi import APIRouter, HTTPException, status

from app.core.config import settings
from app.domain.models import (
    EmailRequest,
    ImagePathRequest,
    TaskAcceptedResponse,
    TaskStatusResponse,
)
from app.infrastructure.tasks.celery_app import celery_app
from app.infrastructure.tasks.ocr_tasks import analyze_document, send_email_notification

router = APIRouter(prefix="/api/v1", tags=["ocr"])


@router.get("/health")
async def health_check():
    return {"status": "ААААААААААААААА"}


@router.post(
    "/analyze_doc",
    response_model=TaskAcceptedResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def analyze_doc(request: ImagePathRequest):
    task = analyze_document.delay(request.image_path)
    return TaskAcceptedResponse(task_id=task.id)


@router.post(
    "/send_message_to_email",
    response_model=TaskAcceptedResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def send_message_to_email(request: EmailRequest):
    task = send_email_notification.delay(
        request.recipient_email,
        request.image_path,
        request.extracted_text,
    )
    return TaskAcceptedResponse(task_id=task.id)


@router.post(
    "/analyze_doc_by_id",
    response_model=TaskAcceptedResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def analyze_doc_by_id(
    photo_id: int,
):
    url = f"{settings.DJANGO_BASE_URL.rstrip('/')}/api/photo/{photo_id}/path/"

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(url)
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail="Django service unavailable") from exc

    if response.status_code == 404:
        raise HTTPException(status_code=404, detail=f"Photo with ID {photo_id} not found")
    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="Unexpected response from Django service")

    image_path = response.json().get("path")
    if not image_path:
        raise HTTPException(status_code=502, detail="Django response does not contain photo path")

    task = analyze_document.delay(image_path)

    return TaskAcceptedResponse(task_id=task.id)


@router.get("/tasks/{task_id}", response_model=TaskStatusResponse)
async def task_status(task_id: str):
    task = AsyncResult(task_id, app=celery_app)
    response = TaskStatusResponse(task_id=task_id, status=task.status.lower())

    if task.successful():
        response.result = task.result
    elif task.failed():
        response.error = str(task.result)

    return response
