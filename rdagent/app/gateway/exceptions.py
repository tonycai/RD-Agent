"""Custom exceptions for RD-Agent Gateway."""

from typing import Optional
from fastapi import HTTPException


class RDAgentGatewayException(Exception):
    """Base exception for RD-Agent Gateway."""
    
    def __init__(self, message: str, error_type: str = "internal_error", code: str = "unknown_error"):
        self.message = message
        self.error_type = error_type
        self.code = code
        super().__init__(message)


class ModelNotFoundError(RDAgentGatewayException):
    """Raised when a requested model is not found."""
    
    def __init__(self, model_id: str):
        super().__init__(
            message=f"Model '{model_id}' not found",
            error_type="invalid_request_error",
            code="model_not_found"
        )


class ScenarioExecutionError(RDAgentGatewayException):
    """Raised when RD-Agent scenario execution fails."""
    
    def __init__(self, scenario: str, error: str):
        super().__init__(
            message=f"Scenario '{scenario}' execution failed: {error}",
            error_type="internal_error",
            code="scenario_execution_error"
        )


class ValidationError(RDAgentGatewayException):
    """Raised when request validation fails."""
    
    def __init__(self, param: str, message: str):
        super().__init__(
            message=f"Invalid parameter '{param}': {message}",
            error_type="invalid_request_error",
            code="validation_error"
        )


class AuthenticationError(RDAgentGatewayException):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            error_type="invalid_request_error",
            code="authentication_error"
        )


class RateLimitError(RDAgentGatewayException):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(
            message=message,
            error_type="rate_limit_error",
            code="rate_limit_exceeded"
        )


def create_openai_error_response(
    status_code: int,
    message: str,
    error_type: str = "internal_error",
    param: Optional[str] = None,
    code: Optional[str] = None
) -> HTTPException:
    """Create an OpenAI-compatible error response."""
    return HTTPException(
        status_code=status_code,
        detail={
            "error": {
                "message": message,
                "type": error_type,
                "param": param,
                "code": code
            }
        }
    )


def exception_to_http_exception(exc: RDAgentGatewayException) -> HTTPException:
    """Convert RD-Agent Gateway exception to HTTP exception."""
    status_code = 500  # Default to internal server error
    
    if exc.error_type == "invalid_request_error":
        status_code = 400
    elif exc.error_type == "authentication_error":
        status_code = 401
    elif exc.error_type == "rate_limit_error":
        status_code = 429
    elif exc.error_type == "internal_error":
        status_code = 500
    
    return create_openai_error_response(
        status_code=status_code,
        message=exc.message,
        error_type=exc.error_type,
        code=exc.code
    )