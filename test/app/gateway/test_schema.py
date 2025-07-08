"""
Unit tests for RD-Agent Gateway Schema module.
Tests OpenAI-compatible API schemas and validation.
"""

import unittest
from unittest.mock import MagicMock
import pytest
from typing import List, Dict, Any

from pydantic import ValidationError

from rdagent.app.gateway.schema import (
    ChatMessage,
    RDAgentConfig,
    RDAgentChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionChoice,
    ChatCompletionMessage,
    Usage,
    Model,
    ModelList,
    ErrorResponse,
    ErrorDetail
)


@pytest.mark.offline
class TestChatMessage(unittest.TestCase):
    """Test ChatMessage schema."""

    def test_valid_user_message(self):
        """Test valid user message creation."""
        message = ChatMessage(role="user", content="Hello, world!")
        self.assertEqual(message.role, "user")
        self.assertEqual(message.content, "Hello, world!")
        self.assertIsNone(message.name)

    def test_valid_assistant_message(self):
        """Test valid assistant message creation."""
        message = ChatMessage(role="assistant", content="Hello! How can I help you?")
        self.assertEqual(message.role, "assistant")
        self.assertEqual(message.content, "Hello! How can I help you?")

    def test_valid_system_message(self):
        """Test valid system message creation."""
        message = ChatMessage(role="system", content="You are a helpful assistant.")
        self.assertEqual(message.role, "system")
        self.assertEqual(message.content, "You are a helpful assistant.")

    def test_message_with_name(self):
        """Test message with optional name field."""
        message = ChatMessage(role="user", content="Hello", name="test_user")
        self.assertEqual(message.name, "test_user")

    def test_invalid_role(self):
        """Test invalid role validation."""
        with self.assertRaises(ValidationError):
            ChatMessage(role="invalid_role", content="Hello")

    def test_empty_content(self):
        """Test that empty content is allowed."""
        message = ChatMessage(role="user", content="")
        self.assertEqual(message.content, "")

    def test_none_content(self):
        """Test that None content raises validation error."""
        with self.assertRaises(ValidationError):
            ChatMessage(role="user", content=None)


@pytest.mark.offline
class TestRDAgentConfig(unittest.TestCase):
    """Test RD-Agent specific configuration schema."""

    def test_data_science_config(self):
        """Test data science configuration."""
        config = RDAgentConfig(
            competition="sf-crime",
            steps=3
        )
        self.assertEqual(config.competition, "sf-crime")
        self.assertEqual(config.steps, 3)
        self.assertIsNone(config.mode)
        self.assertIsNone(config.paper_url)

    def test_quantitative_finance_config(self):
        """Test quantitative finance configuration."""
        config = RDAgentConfig(
            mode="factor",
            steps=2
        )
        self.assertEqual(config.mode, "factor")
        self.assertEqual(config.steps, 2)
        self.assertIsNone(config.competition)

    def test_general_model_config(self):
        """Test general model configuration."""
        config = RDAgentConfig(
            paper_url="https://arxiv.org/abs/1706.03762",
            steps=1
        )
        self.assertEqual(config.paper_url, "https://arxiv.org/abs/1706.03762")
        self.assertEqual(config.steps, 1)

    def test_minimal_config(self):
        """Test minimal configuration with defaults."""
        config = RDAgentConfig()
        self.assertIsNone(config.competition)
        self.assertIsNone(config.mode)
        self.assertIsNone(config.paper_url)
        self.assertEqual(config.steps, 1)  # Default value

    def test_all_fields_config(self):
        """Test configuration with all fields."""
        config = RDAgentConfig(
            competition="titanic",
            mode="model",
            paper_url="https://example.com/paper.pdf",
            steps=5
        )
        self.assertEqual(config.competition, "titanic")
        self.assertEqual(config.mode, "model")
        self.assertEqual(config.paper_url, "https://example.com/paper.pdf")
        self.assertEqual(config.steps, 5)

    def test_negative_steps(self):
        """Test that negative steps are handled."""
        # Depending on validation rules, this might be allowed or not
        config = RDAgentConfig(steps=-1)
        self.assertEqual(config.steps, -1)

    def test_zero_steps(self):
        """Test zero steps configuration."""
        config = RDAgentConfig(steps=0)
        self.assertEqual(config.steps, 0)


@pytest.mark.offline
class TestRDAgentChatCompletionRequest(unittest.TestCase):
    """Test RD-Agent chat completion request schema."""

    def setUp(self):
        """Set up test data."""
        self.valid_messages = [
            ChatMessage(role="user", content="Hello, world!")
        ]

    def test_minimal_request(self):
        """Test minimal valid request."""
        request = RDAgentChatCompletionRequest(
            model="rd-agent-data-science",
            messages=self.valid_messages
        )
        self.assertEqual(request.model, "rd-agent-data-science")
        self.assertEqual(len(request.messages), 1)
        self.assertFalse(request.stream)  # Default value
        self.assertIsNone(request.rd_agent)

    def test_complete_request(self):
        """Test request with all fields."""
        rd_agent_config = RDAgentConfig(competition="sf-crime", steps=3)
        request = RDAgentChatCompletionRequest(
            model="rd-agent-data-science",
            messages=self.valid_messages,
            max_tokens=1000,
            temperature=0.7,
            top_p=0.9,
            n=1,
            stream=True,
            stop=["END"],
            presence_penalty=0.1,
            frequency_penalty=0.2,
            user="test_user",
            rd_agent=rd_agent_config
        )
        
        self.assertEqual(request.model, "rd-agent-data-science")
        self.assertEqual(request.max_tokens, 1000)
        self.assertEqual(request.temperature, 0.7)
        self.assertEqual(request.top_p, 0.9)
        self.assertEqual(request.n, 1)
        self.assertTrue(request.stream)
        self.assertEqual(request.stop, ["END"])
        self.assertEqual(request.presence_penalty, 0.1)
        self.assertEqual(request.frequency_penalty, 0.2)
        self.assertEqual(request.user, "test_user")
        self.assertIsNotNone(request.rd_agent)
        self.assertEqual(request.rd_agent.competition, "sf-crime")

    def test_empty_messages(self):
        """Test that empty messages list raises validation error."""
        with self.assertRaises(ValidationError):
            RDAgentChatCompletionRequest(
                model="rd-agent-data-science",
                messages=[]
            )

    def test_invalid_model(self):
        """Test with empty model name."""
        with self.assertRaises(ValidationError):
            RDAgentChatCompletionRequest(
                model="",
                messages=self.valid_messages
            )

    def test_temperature_bounds(self):
        """Test temperature validation bounds."""
        # Valid temperature
        request = RDAgentChatCompletionRequest(
            model="rd-agent-data-science",
            messages=self.valid_messages,
            temperature=0.5
        )
        self.assertEqual(request.temperature, 0.5)
        
        # Test boundary values if validation exists
        request = RDAgentChatCompletionRequest(
            model="rd-agent-data-science", 
            messages=self.valid_messages,
            temperature=0.0
        )
        self.assertEqual(request.temperature, 0.0)

    def test_multiple_messages(self):
        """Test request with multiple messages."""
        messages = [
            ChatMessage(role="system", content="You are a helpful assistant."),
            ChatMessage(role="user", content="Hello!"),
            ChatMessage(role="assistant", content="Hi there!"),
            ChatMessage(role="user", content="How are you?")
        ]
        
        request = RDAgentChatCompletionRequest(
            model="rd-agent-data-science",
            messages=messages
        )
        self.assertEqual(len(request.messages), 4)

    def test_stop_as_string(self):
        """Test stop parameter as string."""
        request = RDAgentChatCompletionRequest(
            model="rd-agent-data-science",
            messages=self.valid_messages,
            stop="END"
        )
        self.assertEqual(request.stop, "END")

    def test_stop_as_list(self):
        """Test stop parameter as list."""
        request = RDAgentChatCompletionRequest(
            model="rd-agent-data-science", 
            messages=self.valid_messages,
            stop=["END", "STOP", "\n"]
        )
        self.assertEqual(request.stop, ["END", "STOP", "\n"])


@pytest.mark.offline
class TestChatCompletionResponse(unittest.TestCase):
    """Test chat completion response schema."""

    def test_basic_response(self):
        """Test basic response creation."""
        message = ChatCompletionMessage(role="assistant", content="Hello!")
        choice = ChatCompletionChoice(
            index=0,
            message=message,
            finish_reason="stop"
        )
        usage = Usage(prompt_tokens=10, completion_tokens=5, total_tokens=15)
        
        response = ChatCompletionResponse(
            id="chatcmpl-123",
            object="chat.completion",
            created=1234567890,
            model="rd-agent-data-science",
            choices=[choice],
            usage=usage
        )
        
        self.assertEqual(response.id, "chatcmpl-123")
        self.assertEqual(response.object, "chat.completion")
        self.assertEqual(response.created, 1234567890)
        self.assertEqual(response.model, "rd-agent-data-science")
        self.assertEqual(len(response.choices), 1)
        self.assertEqual(response.choices[0].message.content, "Hello!")
        self.assertEqual(response.usage.total_tokens, 15)

    def test_multiple_choices(self):
        """Test response with multiple choices."""
        choices = []
        for i in range(3):
            message = ChatCompletionMessage(role="assistant", content=f"Response {i}")
            choice = ChatCompletionChoice(
                index=i,
                message=message,
                finish_reason="stop"
            )
            choices.append(choice)
        
        usage = Usage(prompt_tokens=10, completion_tokens=15, total_tokens=25)
        response = ChatCompletionResponse(
            id="chatcmpl-multi",
            object="chat.completion",
            created=1234567890,
            model="rd-agent-data-science",
            choices=choices,
            usage=usage
        )
        
        self.assertEqual(len(response.choices), 3)
        for i, choice in enumerate(response.choices):
            self.assertEqual(choice.index, i)
            self.assertEqual(choice.message.content, f"Response {i}")


@pytest.mark.offline  
class TestUsage(unittest.TestCase):
    """Test usage tracking schema."""

    def test_usage_creation(self):
        """Test usage object creation."""
        usage = Usage(prompt_tokens=100, completion_tokens=50, total_tokens=150)
        self.assertEqual(usage.prompt_tokens, 100)
        self.assertEqual(usage.completion_tokens, 50)
        self.assertEqual(usage.total_tokens, 150)

    def test_zero_tokens(self):
        """Test usage with zero tokens."""
        usage = Usage(prompt_tokens=0, completion_tokens=0, total_tokens=0)
        self.assertEqual(usage.prompt_tokens, 0)
        self.assertEqual(usage.completion_tokens, 0)
        self.assertEqual(usage.total_tokens, 0)


@pytest.mark.offline
class TestModel(unittest.TestCase):
    """Test model schema."""

    def test_model_creation(self):
        """Test model object creation."""
        model = Model(
            id="rd-agent-data-science",
            object="model",
            created=1234567890,
            owned_by="microsoft"
        )
        self.assertEqual(model.id, "rd-agent-data-science")
        self.assertEqual(model.object, "model")
        self.assertEqual(model.created, 1234567890)
        self.assertEqual(model.owned_by, "microsoft")

    def test_model_with_optional_fields(self):
        """Test model with optional fields."""
        model = Model(
            id="rd-agent-data-science",
            object="model", 
            created=1234567890,
            owned_by="microsoft",
            root="data_science",
            parent="base-model"
        )
        self.assertEqual(model.root, "data_science")
        self.assertEqual(model.parent, "base-model")


@pytest.mark.offline
class TestModelList(unittest.TestCase):
    """Test model list schema."""

    def test_model_list_creation(self):
        """Test model list creation."""
        models = [
            Model(id="model1", object="model", created=123, owned_by="test"),
            Model(id="model2", object="model", created=124, owned_by="test")
        ]
        
        model_list = ModelList(object="list", data=models)
        self.assertEqual(model_list.object, "list")
        self.assertEqual(len(model_list.data), 2)
        self.assertEqual(model_list.data[0].id, "model1")
        self.assertEqual(model_list.data[1].id, "model2")

    def test_empty_model_list(self):
        """Test empty model list."""
        model_list = ModelList(object="list", data=[])
        self.assertEqual(len(model_list.data), 0)


@pytest.mark.offline
class TestErrorResponse(unittest.TestCase):
    """Test error response schema."""

    def test_error_response_creation(self):
        """Test error response creation."""
        error_detail = ErrorDetail(
            message="Invalid request",
            type="invalid_request_error",
            code="invalid_parameter"
        )
        
        error_response = ErrorResponse(error=error_detail)
        self.assertEqual(error_response.error.message, "Invalid request")
        self.assertEqual(error_response.error.type, "invalid_request_error")
        self.assertEqual(error_response.error.code, "invalid_parameter")

    def test_error_detail_minimal(self):
        """Test error detail with minimal fields."""
        error_detail = ErrorDetail(message="Something went wrong")
        self.assertEqual(error_detail.message, "Something went wrong")
        self.assertIsNone(error_detail.type)
        self.assertIsNone(error_detail.code)
        self.assertIsNone(error_detail.param)


@pytest.mark.offline  
class TestSchemaIntegration(unittest.TestCase):
    """Test schema integration and complex scenarios."""

    def test_full_request_response_cycle(self):
        """Test complete request-response cycle schemas."""
        # Create request
        messages = [
            ChatMessage(role="user", content="Start sf-crime competition")
        ]
        rd_agent_config = RDAgentConfig(competition="sf-crime", steps=3)
        
        request = RDAgentChatCompletionRequest(
            model="rd-agent-data-science",
            messages=messages,
            max_tokens=1000,
            rd_agent=rd_agent_config
        )
        
        # Validate request
        self.assertEqual(request.model, "rd-agent-data-science")
        self.assertEqual(request.rd_agent.competition, "sf-crime")
        
        # Create response
        response_message = ChatCompletionMessage(
            role="assistant",
            content="Starting work on sf-crime competition..."
        )
        choice = ChatCompletionChoice(
            index=0,
            message=response_message,
            finish_reason="stop"
        )
        usage = Usage(prompt_tokens=50, completion_tokens=100, total_tokens=150)
        
        response = ChatCompletionResponse(
            id="chatcmpl-test",
            object="chat.completion",
            created=1234567890,
            model="rd-agent-data-science",
            choices=[choice],
            usage=usage
        )
        
        # Validate response
        self.assertEqual(response.model, "rd-agent-data-science")
        self.assertEqual(response.choices[0].message.content, 
                        "Starting work on sf-crime competition...")

    def test_schema_serialization(self):
        """Test that schemas can be serialized to dict."""
        message = ChatMessage(role="user", content="Hello")
        message_dict = message.model_dump()
        
        self.assertIsInstance(message_dict, dict)
        self.assertEqual(message_dict["role"], "user")
        self.assertEqual(message_dict["content"], "Hello")

    def test_schema_from_dict(self):
        """Test creating schemas from dictionaries."""
        message_data = {
            "role": "assistant",
            "content": "Hello! How can I help you?"
        }
        
        message = ChatMessage(**message_data)
        self.assertEqual(message.role, "assistant")
        self.assertEqual(message.content, "Hello! How can I help you?")


if __name__ == '__main__':
    unittest.main()