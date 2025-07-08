"""Base model classes for RD-Agent Gateway."""

from abc import ABC, abstractmethod
from typing import AsyncGenerator, Dict, Any, List, Optional
import logging
from ..schema import (
    ChatCompletionRequest, 
    ChatCompletionResponse, 
    ChatCompletionChunk,
    RDAgentChatCompletionRequest,
    Model
)

logger = logging.getLogger(__name__)


class BaseRDAgentModel(ABC):
    """Abstract base class for RD-Agent models."""
    
    def __init__(self, model_id: str):
        self.model_id = model_id
        self.logger = logging.getLogger(f"{__name__}.{model_id}")
    
    @abstractmethod
    async def chat_completion(
        self, 
        request: RDAgentChatCompletionRequest
    ) -> ChatCompletionResponse:
        """Generate a chat completion response."""
        pass
    
    @abstractmethod
    async def chat_completion_stream(
        self, 
        request: RDAgentChatCompletionRequest
    ) -> AsyncGenerator[ChatCompletionChunk, None]:
        """Generate a streaming chat completion response."""
        pass
    
    @abstractmethod
    def validate_request(self, request: RDAgentChatCompletionRequest) -> None:
        """Validate the request for this model."""
        pass
    
    @abstractmethod
    def get_model_info(self) -> Model:
        """Get model information."""
        pass
    
    def _parse_messages(self, request: RDAgentChatCompletionRequest) -> List[Dict[str, Any]]:
        """Parse messages from OpenAI format to internal format."""
        parsed_messages = []
        
        for message in request.messages:
            if hasattr(message, 'model_dump'):
                msg_dict = message.model_dump()
            else:
                msg_dict = dict(message)
            parsed_messages.append(msg_dict)
            
        return parsed_messages
    
    def _extract_system_prompt(self, request: RDAgentChatCompletionRequest) -> Optional[str]:
        """Extract system prompt from messages."""
        for message in request.messages:
            if message.role == "system":
                return message.content
        return None
    
    def _extract_user_content(self, request: RDAgentChatCompletionRequest) -> str:
        """Extract user content from the last user message."""
        for message in reversed(request.messages):
            if message.role == "user":
                if isinstance(message.content, str):
                    return message.content
                elif isinstance(message.content, list):
                    # Handle multi-modal content
                    text_parts = []
                    for part in message.content:
                        if isinstance(part, dict) and part.get("type") == "text":
                            text_parts.append(part.get("text", ""))
                    return " ".join(text_parts)
        return ""
    
    def _calculate_usage(self, prompt: str, completion: str) -> Dict[str, int]:
        """Calculate token usage (simplified)."""
        # Simplified token calculation - in production, use a proper tokenizer
        prompt_tokens = len(prompt.split()) * 1.3  # Rough approximation
        completion_tokens = len(completion.split()) * 1.3
        
        return {
            "prompt_tokens": int(prompt_tokens),
            "completion_tokens": int(completion_tokens),
            "total_tokens": int(prompt_tokens + completion_tokens)
        }


class ModelManager:
    """Manages available models and their instances."""
    
    def __init__(self):
        self._models: Dict[str, BaseRDAgentModel] = {}
        self.logger = logging.getLogger(__name__)
    
    def register_model(self, model: BaseRDAgentModel) -> None:
        """Register a model instance."""
        self._models[model.model_id] = model
        self.logger.info(f"Registered model: {model.model_id}")
    
    def get_model(self, model_id: str) -> Optional[BaseRDAgentModel]:
        """Get a model instance by ID."""
        return self._models.get(model_id)
    
    def list_models(self) -> List[Model]:
        """List all available models."""
        models = []
        for model in self._models.values():
            try:
                models.append(model.get_model_info())
            except Exception as e:
                self.logger.error(f"Error getting model info for {model.model_id}: {e}")
        return models
    
    def is_model_available(self, model_id: str) -> bool:
        """Check if a model is available."""
        return model_id in self._models


# Global model manager instance
model_manager = ModelManager()