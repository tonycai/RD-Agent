"""Chat completions router for RD-Agent Gateway."""

import json
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import Union, Optional

from ..auth import get_current_user
from ..schema import (
    RDAgentChatCompletionRequest,
    ChatCompletionResponse,
    ErrorResponse
)
from ..models.base import model_manager

router = APIRouter()


@router.post("/v1/chat/completions")
async def chat_completions(
    request: RDAgentChatCompletionRequest,
    user: Optional[str] = Depends(get_current_user)
) -> Union[ChatCompletionResponse, StreamingResponse]:
    """Create a chat completion."""
    
    # Get the model
    model = model_manager.get_model(request.model)
    if not model:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "message": f"Model '{request.model}' not found",
                    "type": "invalid_request_error",
                    "param": "model",
                    "code": "model_not_found"
                }
            }
        )
    
    try:
        if request.stream:
            # Streaming response
            async def generate():
                async for chunk in model.chat_completion_stream(request):
                    # Convert chunk to JSON and format for SSE
                    chunk_json = chunk.model_dump_json()
                    yield f"data: {chunk_json}\n\n"
                
                # Send the final [DONE] marker
                yield "data: [DONE]\n\n"
            
            return StreamingResponse(
                generate(),
                media_type="text/plain",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Content-Type": "text/plain; charset=utf-8"
                }
            )
        else:
            # Non-streaming response
            return await model.chat_completion(request)
            
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "message": f"Internal server error: {str(e)}",
                    "type": "internal_error",
                    "code": "internal_server_error"
                }
            }
        )