"""RD-Agent specific model implementation."""

import asyncio
import json
import time
import uuid
from typing import AsyncGenerator, Dict, Any, Optional
from fastapi import HTTPException

from .base import BaseRDAgentModel
from ..schema import (
    ChatCompletionResponse,
    ChatCompletionChunk,
    ChatCompletionChoice,
    ChatCompletionChunkChoice,
    ChatCompletionMessage,
    ChatCompletionChunkDelta,
    ChatCompletionUsage,
    RDAgentChatCompletionRequest,
    Model
)
from ..settings import get_scenario_config, get_settings

# Import RD-Agent components
from rdagent.app.data_science.conf import DS_RD_SETTING
from rdagent.scenarios.data_science.loop import DataScienceRDLoop


class RDAgentModel(BaseRDAgentModel):
    """RD-Agent model implementation."""
    
    def __init__(self, model_id: str):
        super().__init__(model_id)
        self.scenario_config = get_scenario_config()
        self.settings = get_settings()
        
        # Get scenario info from model ID
        self.scenario_info = self.scenario_config.get_scenario_by_model(model_id)
        if not self.scenario_info:
            raise ValueError(f"Unknown model ID: {model_id}")
    
    def validate_request(self, request: RDAgentChatCompletionRequest) -> None:
        """Validate the request for this model."""
        if not request.messages:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": {
                        "message": "At least one message is required",
                        "type": "invalid_request_error",
                        "param": "messages",
                        "code": "missing_required_parameter"
                    }
                }
            )
        
        # Validate steps parameter
        if request.rd_agent and request.rd_agent.steps:
            if request.rd_agent.steps > self.settings.max_steps:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "error": {
                            "message": f"Maximum steps allowed: {self.settings.max_steps}",
                            "type": "invalid_request_error",
                            "param": "rd_agent.steps",
                            "code": "parameter_out_of_range"
                        }
                    }
                )
    
    def get_model_info(self) -> Model:
        """Get model information."""
        return Model(
            id=self.model_id,
            owned_by="microsoft",
            root=self.scenario_info["id"]
        )
    
    async def chat_completion(
        self, 
        request: RDAgentChatCompletionRequest
    ) -> ChatCompletionResponse:
        """Generate a chat completion response."""
        self.validate_request(request)
        
        # Extract parameters
        steps = 1
        if request.rd_agent and request.rd_agent.steps:
            steps = request.rd_agent.steps
            
        competition = self._get_competition(request)
        
        # Run RD-Agent scenario
        results = []
        try:
            async for result in self._run_scenario(request, steps, competition):
                results.append(str(result))
        except Exception as e:
            self.logger.error(f"Error running scenario: {e}")
            raise HTTPException(
                status_code=500,
                detail={
                    "error": {
                        "message": f"Internal error running RD-Agent scenario: {str(e)}",
                        "type": "internal_error",
                        "code": "scenario_execution_error"
                    }
                }
            )
        
        # Build response
        content = "\n".join(results) if results else "RD-Agent scenario completed successfully."
        prompt_content = self._extract_user_content(request)
        usage = self._calculate_usage(prompt_content, content)
        
        return ChatCompletionResponse(
            id=f"chatcmpl-{uuid.uuid4().hex[:8]}",
            model=request.model,
            choices=[
                ChatCompletionChoice(
                    index=0,
                    message=ChatCompletionMessage(
                        role="assistant",
                        content=content
                    ),
                    finish_reason="stop"
                )
            ],
            usage=ChatCompletionUsage(**usage)
        )
    
    async def chat_completion_stream(
        self, 
        request: RDAgentChatCompletionRequest
    ) -> AsyncGenerator[ChatCompletionChunk, None]:
        """Generate a streaming chat completion response."""
        self.validate_request(request)
        
        # Extract parameters
        steps = 1
        if request.rd_agent and request.rd_agent.steps:
            steps = request.rd_agent.steps
            
        competition = self._get_competition(request)
        
        # Generate unique ID for this completion
        completion_id = f"chatcmpl-{uuid.uuid4().hex[:8]}"
        
        try:
            # Stream results from RD-Agent
            async for result in self._run_scenario(request, steps, competition):
                yield ChatCompletionChunk(
                    id=completion_id,
                    model=request.model,
                    choices=[
                        ChatCompletionChunkChoice(
                            index=0,
                            delta=ChatCompletionChunkDelta(
                                role="assistant",
                                content=str(result)
                            )
                        )
                    ]
                )
                
                # Add a small delay to prevent overwhelming the client
                await asyncio.sleep(0.1)
            
            # Send final chunk with finish_reason
            yield ChatCompletionChunk(
                id=completion_id,
                model=request.model,
                choices=[
                    ChatCompletionChunkChoice(
                        index=0,
                        delta=ChatCompletionChunkDelta(),
                        finish_reason="stop"
                    )
                ]
            )
            
        except Exception as e:
            self.logger.error(f"Error in streaming scenario: {e}")
            # Send error chunk
            yield ChatCompletionChunk(
                id=completion_id,
                model=request.model,
                choices=[
                    ChatCompletionChunkChoice(
                        index=0,
                        delta=ChatCompletionChunkDelta(
                            role="assistant",
                            content=f"Error: {str(e)}"
                        ),
                        finish_reason="stop"
                    )
                ]
            )
    
    def _get_competition(self, request: RDAgentChatCompletionRequest) -> str:
        """Extract competition name from request."""
        # Priority order: rd_agent.competition -> model suffix -> default
        
        if request.rd_agent and request.rd_agent.competition:
            return request.rd_agent.competition
        
        # Extract from model name (e.g., "rd-agent-sf-crime")
        if request.model.startswith("rd-agent-") and len(request.model.split("-")) > 2:
            suffix = "-".join(request.model.split("-")[2:])
            return suffix
        
        return self.settings.default_competition
    
    async def _run_scenario(
        self, 
        request: RDAgentChatCompletionRequest, 
        steps: int, 
        competition: str
    ) -> AsyncGenerator[str, None]:
        """Run the appropriate RD-Agent scenario."""
        scenario_type = self.scenario_info["type"]
        
        if scenario_type == "data_science":
            async for result in self._run_data_science_scenario(steps, competition):
                yield result
        elif scenario_type == "quantitative_finance":
            async for result in self._run_quant_scenario(request, steps):
                yield result
        elif scenario_type == "general_model":
            async for result in self._run_general_model_scenario(request, steps):
                yield result
        else:
            raise ValueError(f"Unknown scenario type: {scenario_type}")
    
    async def _run_data_science_scenario(
        self, 
        steps: int, 
        competition: str
    ) -> AsyncGenerator[str, None]:
        """Run data science scenario."""
        # Configure DS settings
        DS_RD_SETTING.competition = competition
        
        # Create and run the loop
        ds_loop = DataScienceRDLoop(DS_RD_SETTING)
        
        try:
            async for result in ds_loop.run(step_n=steps):
                yield f"[Data Science Step] {result}"
        except Exception as e:
            self.logger.error(f"Error in data science scenario: {e}")
            yield f"[Error] Data Science scenario failed: {str(e)}"
    
    async def _run_quant_scenario(
        self, 
        request: RDAgentChatCompletionRequest, 
        steps: int
    ) -> AsyncGenerator[str, None]:
        """Run quantitative finance scenario."""
        # This is a placeholder - implement based on your quant scenarios
        yield f"[Quantitative Finance] Starting scenario with {steps} steps"
        
        for i in range(steps):
            await asyncio.sleep(1)  # Simulate work
            yield f"[Quant Step {i+1}] Processing financial data and models..."
        
        yield "[Quantitative Finance] Scenario completed successfully"
    
    async def _run_general_model_scenario(
        self, 
        request: RDAgentChatCompletionRequest, 
        steps: int
    ) -> AsyncGenerator[str, None]:
        """Run general model scenario."""
        # Extract paper URL from user content if available
        user_content = self._extract_user_content(request)
        
        yield f"[General Model] Starting paper implementation with {steps} steps"
        yield f"[General Model] Processing content: {user_content[:100]}..."
        
        for i in range(steps):
            await asyncio.sleep(1)  # Simulate work
            yield f"[Model Step {i+1}] Analyzing paper and implementing model..."
        
        yield "[General Model] Model implementation completed successfully"