"""OpenAI-compatible API schema definitions for RD-Agent Gateway."""

from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field
import time


# Message Types
class SystemMessage(BaseModel):
    role: Literal["system"] = "system"
    content: str


class UserMessage(BaseModel):
    role: Literal["user"] = "user"
    content: Union[str, List[Dict[str, Any]]]


class AssistantMessage(BaseModel):
    role: Literal["assistant"] = "assistant"
    content: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None


class ToolMessage(BaseModel):
    role: Literal["tool"] = "tool"
    content: str
    tool_call_id: str


Message = Union[SystemMessage, UserMessage, AssistantMessage, ToolMessage]


# Function and Tool Definitions
class FunctionParameters(BaseModel):
    type: Literal["object"] = "object"
    properties: Dict[str, Any]
    required: Optional[List[str]] = None


class Function(BaseModel):
    name: str
    description: Optional[str] = None
    parameters: Optional[FunctionParameters] = None


class Tool(BaseModel):
    type: Literal["function"] = "function"
    function: Function


# Chat Completion Request
class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    functions: Optional[List[Function]] = None
    function_call: Optional[Union[str, Dict[str, str]]] = None
    tools: Optional[List[Tool]] = None
    tool_choice: Optional[Union[str, Dict[str, Any]]] = None
    temperature: Optional[float] = Field(default=1.0, ge=0.0, le=2.0)
    top_p: Optional[float] = Field(default=1.0, ge=0.0, le=1.0)
    n: Optional[int] = Field(default=1, ge=1, le=128)
    stream: Optional[bool] = False
    stop: Optional[Union[str, List[str]]] = None
    max_tokens: Optional[int] = Field(default=None, gt=0)
    presence_penalty: Optional[float] = Field(default=0.0, ge=-2.0, le=2.0)
    frequency_penalty: Optional[float] = Field(default=0.0, ge=-2.0, le=2.0)
    logit_bias: Optional[Dict[str, float]] = None
    user: Optional[str] = None


# Chat Completion Response
class ChatCompletionUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatCompletionMessage(BaseModel):
    role: Literal["assistant"]
    content: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    function_call: Optional[Dict[str, Any]] = None


class ChatCompletionChoice(BaseModel):
    index: int
    message: ChatCompletionMessage
    finish_reason: Optional[Literal["stop", "length", "function_call", "tool_calls", "content_filter"]]


class ChatCompletionResponse(BaseModel):
    id: str
    object: Literal["chat.completion"] = "chat.completion"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str
    choices: List[ChatCompletionChoice]
    usage: ChatCompletionUsage
    system_fingerprint: Optional[str] = None


# Streaming Response
class ChatCompletionChunkDelta(BaseModel):
    role: Optional[Literal["assistant"]] = None
    content: Optional[str] = None
    function_call: Optional[Dict[str, Any]] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None


class ChatCompletionChunkChoice(BaseModel):
    index: int
    delta: ChatCompletionChunkDelta
    finish_reason: Optional[Literal["stop", "length", "function_call", "tool_calls", "content_filter"]] = None


class ChatCompletionChunk(BaseModel):
    id: str
    object: Literal["chat.completion.chunk"] = "chat.completion.chunk"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str
    choices: List[ChatCompletionChunkChoice]
    system_fingerprint: Optional[str] = None


# Model Listing
class Model(BaseModel):
    id: str
    object: Literal["model"] = "model"
    created: int = Field(default_factory=lambda: int(time.time()))
    owned_by: str
    permission: Optional[List[Dict[str, Any]]] = None
    root: Optional[str] = None
    parent: Optional[str] = None


class ModelList(BaseModel):
    object: Literal["list"] = "list"
    data: List[Model]


# Error Responses
class ErrorDetail(BaseModel):
    message: str
    type: str
    param: Optional[str] = None
    code: Optional[str] = None


class ErrorResponse(BaseModel):
    error: ErrorDetail


# RD-Agent Specific Extensions
class RDAgentScenario(BaseModel):
    """RD-Agent scenario configuration."""
    id: str
    type: Literal["data_science", "quantitative_finance", "general_model"]
    description: str
    parameters: Optional[Dict[str, Any]] = None


class RDAgentRequest(BaseModel):
    """Extended request for RD-Agent specific functionality."""
    scenario: Optional[RDAgentScenario] = None
    competition: Optional[str] = None  # For data science scenarios
    steps: Optional[int] = Field(default=1, ge=1, le=100)
    log_level: Optional[Literal["DEBUG", "INFO", "WARNING", "ERROR"]] = "INFO"


class RDAgentChatCompletionRequest(ChatCompletionRequest):
    """Chat completion request with RD-Agent extensions."""
    rd_agent: Optional[RDAgentRequest] = None


# Health Check
class HealthCheck(BaseModel):
    status: Literal["healthy", "unhealthy"]
    timestamp: int = Field(default_factory=lambda: int(time.time()))
    version: Optional[str] = None
    details: Optional[Dict[str, Any]] = None