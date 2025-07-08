# RD-Agent OpenAI-Compatible Gateway

This directory contains the OpenAI-compatible RESTful API gateway for RD-Agent, enabling seamless integration with existing tools and frameworks that use the OpenAI API format.

## Features

- **OpenAI API Compatibility**: Full compatibility with OpenAI's chat completions API
- **Multiple Scenarios**: Support for data science, quantitative finance, and general model scenarios
- **Streaming Support**: Server-sent events (SSE) for real-time responses
- **Authentication**: Optional bearer token authentication
- **Error Handling**: Comprehensive error handling with OpenAI-compatible error responses
- **Model Management**: Dynamic model discovery and management
- **Health Checks**: Built-in health check endpoints

## Quick Start

### 1. Basic Usage

Start the gateway server:

```bash
# Using the new main module
uvicorn rdagent.app.gateway.main_new:app --host 0.0.0.0 --port 8000

# Or using the existing entry point
uvicorn rdagent.app.gateway.main:app --host 0.0.0.0 --port 8000
```

### 2. Configuration

Set environment variables in `.env` file:

```bash
# Server Configuration
RD_AGENT_HOST=0.0.0.0
RD_AGENT_PORT=8000
RD_AGENT_DEBUG=false

# Authentication (optional)
RD_AGENT_AUTH_ENABLED=true
RD_AGENT_API_KEY=your-api-key-here

# RD-Agent Settings
RD_AGENT_DEFAULT_SCENARIO=data_science
RD_AGENT_DEFAULT_COMPETITION=sf-crime
RD_AGENT_MAX_STEPS=10
```

### 3. API Usage Examples

#### List Available Models

```bash
curl http://localhost:8000/v1/models
```

Response:
```json
{
  "object": "list",
  "data": [
    {
      "id": "rd-agent-data-science",
      "object": "model",
      "created": 1704067200,
      "owned_by": "microsoft"
    },
    {
      "id": "rd-agent-quantitative-finance",
      "object": "model", 
      "created": 1704067200,
      "owned_by": "microsoft"
    }
  ]
}
```

#### Chat Completion (Non-streaming)

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{
    "model": "rd-agent-data-science",
    "messages": [
      {"role": "user", "content": "Start a data science project for sf-crime competition"}
    ],
    "stream": false,
    "rd_agent": {
      "competition": "sf-crime",
      "steps": 3
    }
  }'
```

#### Chat Completion (Streaming)

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{
    "model": "rd-agent-data-science",
    "messages": [
      {"role": "user", "content": "Start a data science project"}
    ],
    "stream": true,
    "rd_agent": {
      "steps": 5
    }
  }'
```

## API Reference

### Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/chat/completions` | POST | Create chat completion |
| `/v1/models` | GET | List available models |
| `/health` | GET | Health check |
| `/docs` | GET | Interactive API documentation |

### Models

Available models and their scenarios:

- `rd-agent-data-science`: Data science and Kaggle competitions
- `rd-agent-quantitative-finance`: Quantitative finance factor and model optimization
- `rd-agent-general-model`: General model implementation from research papers

### RD-Agent Extensions

The gateway supports RD-Agent specific extensions via the `rd_agent` parameter:

```json
{
  "model": "rd-agent-data-science",
  "messages": [...],
  "rd_agent": {
    "scenario": {
      "id": "data_science",
      "type": "data_science",
      "description": "Custom scenario",
      "parameters": {}
    },
    "competition": "sf-crime",
    "steps": 5,
    "log_level": "INFO"
  }
}
```

#### RD-Agent Parameters

- `scenario`: Custom scenario configuration
- `competition`: Competition name (for data science scenarios)
- `steps`: Number of execution steps (1-100)
- `log_level`: Logging level (DEBUG, INFO, WARNING, ERROR)

## Error Handling

The gateway returns OpenAI-compatible error responses:

```json
{
  "error": {
    "message": "Model 'invalid-model' not found",
    "type": "invalid_request_error",
    "param": "model",
    "code": "model_not_found"
  }
}
```

### Error Types

- `invalid_request_error`: Invalid request parameters
- `authentication_error`: Authentication failed
- `rate_limit_error`: Rate limit exceeded
- `internal_error`: Internal server error

## Architecture

### Directory Structure

```
rdagent/app/gateway/
├── main_new.py           # New FastAPI application
├── main.py               # Legacy application
├── schema.py             # OpenAI-compatible schemas
├── auth.py               # Authentication middleware
├── settings.py           # Configuration management
├── exceptions.py         # Custom exceptions
├── models/
│   ├── base.py          # Abstract base classes
│   └── rd_agent.py      # RD-Agent implementation
└── routers/
    ├── chat.py          # Chat completions
    ├── models.py        # Model management
    └── health.py        # Health checks
```

### Key Components

1. **Schema Layer** (`schema.py`): OpenAI-compatible Pydantic models
2. **Authentication** (`auth.py`): Bearer token authentication with configurable sources
3. **Model Abstraction** (`models/`): Clean separation between API and business logic
4. **Routing** (`routers/`): Organized endpoint handlers
5. **Error Handling** (`exceptions.py`): Comprehensive error management

## Integration Examples

### Python OpenAI Client

```python
from openai import OpenAI

client = OpenAI(
    api_key="your-api-key",
    base_url="http://localhost:8000/v1"
)

response = client.chat.completions.create(
    model="rd-agent-data-science",
    messages=[
        {"role": "user", "content": "Start sf-crime competition"}
    ],
    extra_body={
        "rd_agent": {
            "competition": "sf-crime",
            "steps": 3
        }
    }
)

print(response.choices[0].message.content)
```

### cURL with Streaming

```bash
curl -N -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-api-key" \
  -d '{
    "model": "rd-agent-data-science",
    "messages": [{"role": "user", "content": "Start data science project"}],
    "stream": true
  }'
```

### LangChain Integration

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    openai_api_key="your-api-key",
    openai_api_base="http://localhost:8000/v1",
    model="rd-agent-data-science"
)

response = llm.invoke("Start a new data science project")
print(response.content)
```

## Development

### Running in Development Mode

```bash
# With auto-reload
uvicorn rdagent.app.gateway.main_new:app --reload --host 0.0.0.0 --port 8000

# With debug logging
RD_AGENT_DEBUG=true RD_AGENT_LOG_LEVEL=DEBUG uvicorn rdagent.app.gateway.main_new:app --reload
```

### Testing

```bash
# Run gateway tests
pytest test/gateway/

# Test specific endpoint
pytest test/gateway/test_chat_completions.py -v
```

### Adding New Scenarios

1. Implement scenario in `rdagent/scenarios/`
2. Add scenario configuration to `settings.py`
3. Update model implementation in `models/rd_agent.py`
4. Register new models in `main_new.py`

## Security

### Authentication

Enable authentication by setting:

```bash
RD_AGENT_AUTH_ENABLED=true
RD_AGENT_API_KEY=your-secure-api-key
```

Multiple API keys can be provided:

```bash
RD_AGENT_API_KEYS=key1,key2,key3
```

### CORS

Configure CORS origins:

```bash
RD_AGENT_CORS_ORIGINS=["http://localhost:3000", "https://yourdomain.com"]
```

### Rate Limiting

Enable rate limiting:

```bash
RD_AGENT_RATE_LIMIT_ENABLED=true
RD_AGENT_RATE_LIMIT_REQUESTS=60
RD_AGENT_RATE_LIMIT_WINDOW=60
```

## Monitoring

### Health Checks

The gateway provides health check endpoints:

```bash
# Basic health check
curl http://localhost:8000/health

# Detailed health check
curl http://localhost:8000/v1/health
```

### Logging

Configure logging levels:

- `DEBUG`: Detailed debug information
- `INFO`: General information (default)
- `WARNING`: Warning messages
- `ERROR`: Error messages only

### Metrics

Metrics can be collected via:

- Request logging middleware
- Custom metrics endpoints
- Integration with monitoring systems (Prometheus, etc.)

## Troubleshooting

### Common Issues

1. **Port already in use**: Change `RD_AGENT_PORT` or kill existing process
2. **Model not found**: Check model registration in startup
3. **Authentication errors**: Verify API key configuration
4. **Scenario execution failures**: Check RD-Agent dependencies and Docker setup

### Debug Mode

Enable debug mode for detailed logging:

```bash
RD_AGENT_DEBUG=true RD_AGENT_LOG_LEVEL=DEBUG uvicorn rdagent.app.gateway.main_new:app
```

### Health Check

Use health check to verify system status:

```bash
curl http://localhost:8000/health
```

This should return `{"status": "healthy"}` if everything is working correctly.