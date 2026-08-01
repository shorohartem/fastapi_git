from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from app.core.config import settings
from app.api.router import router

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting FastAPI OCR Service...")
    app.state.settings = settings
    yield
    print("Shutting down FastAPI OCR Service...")

def create_app() -> FastAPI:
    app = FastAPI(
        title="OCR Service",
        docs_url="/docs",
        description="Анализ ",
        version="1.0.0",
        lifespan=lifespan
    )

    @app.get("/", include_in_schema=False)
    async def swagger_redirect():
        return RedirectResponse(url="/docs")

    @app.get("/health", tags=["system"])
    async def health_check():
        return {"status": "ok"}

    app.include_router(router)
    return app

app = create_app()
