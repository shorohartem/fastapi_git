from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import settings
from app.api.router import router   # если роутер есть — импортируй его

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting FastAPI OCR Service...")
    app.state.settings = settings
    yield
    print("Shutting down FastAPI OCR Service...")

def create_app() -> FastAPI:
    app = FastAPI(
        title="OCR Service",
        description="Анализ изображений через Tesseract и отправка уведомлений",
        version="1.0.0",
        lifespan=lifespan
    )
    app.include_router(router)
    return app

app = create_app()

@app.get("/health")
async def health_check():
    return {"status": True}