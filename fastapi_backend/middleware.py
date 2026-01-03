"""FastAPI middleware for error handling and request logging."""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi_backend.logging_config import logger
import time
import traceback


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for consistent error handling and logging.
    Catches all exceptions and returns a JSON error response.
    """
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        try:
            response = await call_next(request)
            duration = time.time() - start_time
            logger.info(
                f"{request.method} {request.url.path} - "
                f"Status: {response.status_code} - Duration: {duration:.3f}s"
            )
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            error_id = f"{request.method}_{request.url.path}_{int(time.time() * 1000)}"
            
            logger.error(
                f"Exception in {request.method} {request.url.path} "
                f"(Error ID: {error_id}): {str(e)}\n{traceback.format_exc()}"
            )
            
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "Internal Server Error",
                    "error_id": error_id,
                    "details": str(e) if str(e) else "An unexpected error occurred"
                }
            )


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging incoming requests at DEBUG level."""
    
    async def dispatch(self, request: Request, call_next):
        logger.debug(
            f"Incoming: {request.method} {request.url.path} "
            f"from {request.client.host if request.client else 'unknown'}"
        )
        return await call_next(request)
