from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.api.predict import router
from app.core.error_handlers import (
    ScholarshipAPIError,
    scholarship_api_error_handler,
    validation_exception_handler,
    general_exception_handler
)
from fastapi.exceptions import RequestValidationError
from app.core.config import APP_NAME, APP_VERSION
from app.core.logger import get_logger
from datetime import datetime
import os

logger = get_logger("main")

# Path to the project root where index.html lives
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="AI-powered scholarship prediction and recommendation engine"
)

# ✅ CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Global Error Handlers
app.add_exception_handler(ScholarshipAPIError, scholarship_api_error_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)


# ✅ Router
app.include_router(router)

logger.info(f"🚀 {APP_NAME} v{APP_VERSION} initialized")


@app.get("/")
def serve_ui():
    """Serve the main UI"""
    return FileResponse(os.path.join(BASE_DIR, "index.html"))


@app.get("/api/status")
def api_status():
    return {
        "app": APP_NAME,
        "version": APP_VERSION,
        "status": "running",
        "message": "🚀 Scholarship Predictor AI is live!"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": APP_VERSION,
        "services": {
            "api": "operational",
            "llm": "operational",
            "search": "operational"
        }
    }