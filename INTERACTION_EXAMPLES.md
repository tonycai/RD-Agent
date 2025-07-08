# RD-Agent Gateway Interaction Examples

This directory contains comprehensive examples for interacting with the RD-Agent OpenAI-compatible gateway.

## 🚀 Quick Start

### 1. Start the Gateway
```bash
python -m uvicorn rdagent.app.gateway.main_new:app --host 0.0.0.0 --port 8001
```

### 2. Quick Test
```bash
./quick_test.sh
```

## 📜 Available Scripts

### Shell Scripts

#### `interact_examples.sh` - Comprehensive Shell Examples
Full-featured script with multiple testing scenarios:

```bash
# Show all available options
./interact_examples.sh help

# Check gateway status
./interact_examples.sh check

# List available models
./interact_examples.sh models

# Test data science scenario
./interact_examples.sh datasci

# Test quantitative finance scenario  
./interact_examples.sh quant

# Test general model scenario
./interact_examples.sh general

# Test streaming responses
./interact_examples.sh stream

# Show Python client examples
./interact_examples.sh python

# Show additional curl examples
./interact_examples.sh curl

# Run performance test
./interact_examples.sh perf

# Run basic tests (excluding heavy RD-Agent scenarios)
./interact_examples.sh all
```

#### `quick_test.sh` - Simple Health Check
Quick validation that the gateway is working:

```bash
./quick_test.sh
```

### Python Scripts

#### `python_examples.py` - Python Client Examples
Comprehensive Python examples using both requests and OpenAI client:

```bash
# Install requirements
pip install openai requests

# Show available functions
python python_examples.py help

# Test gateway health
python python_examples.py health_check

# List models
python python_examples.py list_models

# Test data science scenario
python python_examples.py data_science_example

# Test quantitative finance scenario
python python_examples.py quantitative_finance_example

# Use OpenAI Python client
python python_examples.py openai_client_example

# Test streaming responses
python python_examples.py streaming_example

# Run all examples
python python_examples.py run_all_examples
```

## 🔌 Direct API Examples

### Health Check
```bash
curl http://localhost:8001/health
```

### List Models
```bash
curl http://localhost:8001/v1/models
```

### Data Science Chat Completion
```bash
curl -X POST http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "rd-agent-data-science",
    "messages": [
      {"role": "user", "content": "Start working on the sf-crime competition"}
    ],
    "rd_agent": {
      "competition": "sf-crime",
      "steps": 3
    }
  }'
```

### Quantitative Finance Example
```bash
curl -X POST http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "rd-agent-quantitative-finance",
    "messages": [
      {"role": "user", "content": "Develop a momentum factor"}
    ],
    "rd_agent": {
      "mode": "factor",
      "steps": 2
    }
  }'
```

### Streaming Response
```bash
curl -X POST http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  --no-buffer \
  -d '{
    "model": "rd-agent-data-science",
    "messages": [
      {"role": "user", "content": "Explain machine learning pipeline"}
    ],
    "stream": true
  }'
```

## 🐍 Python OpenAI Client

```python
from openai import OpenAI

# Initialize client
client = OpenAI(
    api_key="your-api-key",  # Optional if auth disabled
    base_url="http://localhost:8001/v1"
)

# Data Science Example
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

## 🔧 Configuration

### Environment Variables
```bash
# Optional API key (if authentication enabled)
export RD_AGENT_API_KEY="your-api-key"

# Gateway URL (if different from default)
export GATEWAY_URL="http://localhost:8001"
```

### Available Models
- `rd-agent-data-science` - Kaggle competitions and ML pipelines
- `rd-agent-quantitative-finance` - Factor discovery and model optimization  
- `rd-agent-general-model` - Research paper implementation

### RD-Agent Specific Parameters

#### Data Science (`rd-agent-data-science`)
```json
{
  "rd_agent": {
    "competition": "sf-crime",      // Competition name
    "steps": 3                       // Number of steps to execute
  }
}
```

#### Quantitative Finance (`rd-agent-quantitative-finance`)
```json
{
  "rd_agent": {
    "mode": "factor",               // "factor", "model", or "quant"
    "steps": 2                      // Number of steps to execute
  }
}
```

#### General Model (`rd-agent-general-model`)
```json
{
  "rd_agent": {
    "paper_url": "https://arxiv.org/abs/1706.03762",  // Paper URL
    "steps": 2                                         // Number of steps
  }
}
```

## 🚨 Troubleshooting

### Gateway Not Running
```bash
# Check if gateway is accessible
curl -f http://localhost:8001/health

# Start gateway if not running
python -m uvicorn rdagent.app.gateway.main_new:app --host 0.0.0.0 --port 8001
```

### Dependencies Missing
```bash
# For shell scripts
sudo apt-get install jq curl

# For Python scripts  
pip install openai requests
```

### Authentication Issues
If authentication is enabled, ensure you have the API key:
```bash
export RD_AGENT_API_KEY="your-api-key"
```

### Port Conflicts
If port 8001 is in use, start gateway on different port:
```bash
python -m uvicorn rdagent.app.gateway.main_new:app --host 0.0.0.0 --port 8002
```

Then update the gateway URL in scripts:
```bash
export GATEWAY_URL="http://localhost:8002"
```

## 📚 Additional Resources

- [RD-Agent Documentation](../README.md)
- [OpenAI API Reference](https://platform.openai.com/docs/api-reference)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## 🤝 Contributing

Feel free to add more examples or improve existing ones. The scripts are designed to be modular and easy to extend.