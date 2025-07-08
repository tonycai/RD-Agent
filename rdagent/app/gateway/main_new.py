"""
OpenAI-compatible FastAPI Gateway for RD-Agent.

This module provides an OpenAI-compatible RESTful API gateway for RD-Agent,
allowing seamless integration with existing tools and frameworks.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import time

from .settings import get_settings, get_scenario_config
from .models.base import model_manager
from .models.rd_agent import RDAgentModel
from .routers import chat_router, models_router, health_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    logger.info("Starting RD-Agent Gateway...")
    
    settings = get_settings()
    scenario_config = get_scenario_config()
    
    # Register available models
    for model_id in scenario_config.get_models():
        try:
            model = RDAgentModel(model_id)
            model_manager.register_model(model)
            logger.info(f"Registered model: {model_id}")
        except Exception as e:
            logger.error(f"Failed to register model {model_id}: {e}")
    
    logger.info(f"Gateway started with {len(model_manager._models)} models")
    yield
    
    # Shutdown
    logger.info("Shutting down RD-Agent Gateway...")


# Create FastAPI application
app = FastAPI(
    title="RD-Agent Gateway",
    description="OpenAI-compatible API gateway for RD-Agent",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Get settings
settings = get_settings()

# Add CORS middleware
if settings.cors_enabled:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# Custom exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors in OpenAI format."""
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "message": f"Validation error: {str(exc)}",
                "type": "invalid_request_error",
                "param": None,
                "code": "validation_error"
            }
        }
    )


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 errors in OpenAI format."""
    return JSONResponse(
        status_code=404,
        content={
            "error": {
                "message": "Not found",
                "type": "invalid_request_error", 
                "param": None,
                "code": "not_found"
            }
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Handle internal server errors in OpenAI format."""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "message": "Internal server error",
                "type": "internal_error",
                "param": None,
                "code": "internal_server_error"
            }
        }
    )


# Add request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log incoming requests."""
    start_time = time.time()
    
    # Log request
    logger.info(f"Request: {request.method} {request.url.path}")
    
    # Process request
    response = await call_next(request)
    
    # Log response
    process_time = time.time() - start_time
    logger.info(f"Response: {response.status_code} ({process_time:.3f}s)")
    
    return response


# Include routers
app.include_router(chat_router, tags=["Chat Completions"])
app.include_router(models_router, tags=["Models"])
app.include_router(health_router, tags=["Health"])


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "RD-Agent Gateway",
        "version": "1.0.0",
        "description": "OpenAI-compatible API gateway for RD-Agent",
        "endpoints": {
            "chat_completions": "/v1/chat/completions",
            "models": "/v1/models",
            "health": "/health",
            "docs": "/docs"
        }
    }


# Compatibility endpoint for legacy clients
@app.get("/v1")
async def v1_root():
    """OpenAI API v1 root endpoint."""
    return {
        "object": "api.version",
        "version": "1.0.0",
        "name": "RD-Agent Gateway"
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "rdagent.app.gateway.main_new:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )