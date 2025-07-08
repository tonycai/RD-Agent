"""Models router for RD-Agent Gateway."""

from fastapi import APIRouter, Depends
from typing import Optional

from ..auth import get_optional_user
from ..schema import ModelList
from ..models.base import model_manager

router = APIRouter()


@router.get("/v1/models", response_model=ModelList)
async def list_models(user: Optional[str] = Depends(get_optional_user)):
    """List available models."""
    models = model_manager.list_models()
    
    return ModelList(data=models)