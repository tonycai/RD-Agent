"""Health check router for RD-Agent Gateway."""

import time
from fastapi import APIRouter
from ..schema import HealthCheck
from ..settings import get_settings

router = APIRouter()


@router.get("/health", response_model=HealthCheck)
@router.get("/v1/health", response_model=HealthCheck) 
async def health_check():
    """Health check endpoint."""
    settings = get_settings()
    
    # Perform basic health checks
    details = {
        "auth_enabled": settings.auth_enabled,
        "cors_enabled": settings.cors_enabled,
        "debug_mode": settings.debug,
        "default_scenario": settings.default_scenario
    }
    
    return HealthCheck(
        status="healthy",
        details=details
    )