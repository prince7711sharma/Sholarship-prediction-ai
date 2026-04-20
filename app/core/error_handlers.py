from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.core.logger import get_logger

logger = get_logger("error_handler")


# ─── Custom Exceptions ───────────────────────────────────────────────
class ScholarshipAPIError(Exception):
    """Base exception for the Scholarship API."""
    def __init__(self, message: str, status_code: int = 500, details: str = None):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)


class LLMError(ScholarshipAPIError):
    """Raised when the LLM service fails."""
    def __init__(self, message: str = "AI service temporarily unavailable", details: str = None):
        super().__init__(message=message, status_code=503, details=details)


class SearchError(ScholarshipAPIError):
    """Raised when the web search service fails."""
    def __init__(self, message: str = "Scholarship search service unavailable", details: str = None):
        super().__init__(message=message, status_code=503, details=details)


class ValidationError(ScholarshipAPIError):
    """Raised when input validation fails."""
    def __init__(self, message: str = "Invalid input data", details: str = None):
        super().__init__(message=message, status_code=400, details=details)


# ─── Error Response Builder ──────────────────────────────────────────
def build_error_response(status_code: int, message: str, details: str = None):
    """Build a structured error response."""
    response = {
        "status": "error",
        "error": {
            "code": status_code,
            "message": message,
        }
    }
    if details:
        response["error"]["details"] = details
    return JSONResponse(status_code=status_code, content=response)


# ─── Global Exception Handlers ───────────────────────────────────────
async def scholarship_api_error_handler(request: Request, exc: ScholarshipAPIError):
    """Handle custom ScholarshipAPIError exceptions."""
    logger.error(f"{exc.__class__.__name__}: {exc.message} | Details: {exc.details}")
    return build_error_response(exc.status_code, exc.message, exc.details)


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle FastAPI validation errors (422)."""
    errors = exc.errors()
    error_details = []
    
    for err in errors:
        loc = " -> ".join([str(l) for l in err.get("loc", [])])
        msg = err.get("msg", "Unknown error")
        typ = err.get("type", "Unknown type")
        error_details.append(f"Field: {loc} | Error: {msg} ({typ})")
        
    logger.error(f"❌ Validation Failed: {'; '.join(error_details)}")
    
    return build_error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        message="Invalid request data. Please check your inputs.",
        details=error_details[0] if error_details else "Check all fields are correctly filled."
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Catch-all handler for unhandled exceptions."""
    logger.critical(f"Unhandled exception: {type(exc).__name__}: {str(exc)}")
    return build_error_response(
        500,
        "An unexpected error occurred. Please try again later.",
        str(exc) if str(exc) else None
    )

