# RD-Agent Chat Interaction Scripts

This directory contains several bash shell scripts for interacting with the RD-Agent Docker container through its OpenAI-compatible API.

## 📁 Available Scripts

### 1. `chat_interact.sh` - Full-Featured Chat Interface
**Comprehensive interactive chat script with advanced features.**

```bash
# Interactive mode
./chat_interact.sh -i

# Single message
./chat_interact.sh "Hello, what can you help me with?"

# Specify model
./chat_interact.sh -m rd-agent-quantitative-finance "Explain factor models"

# With scenario
./chat_interact.sh -s data_science "Help with Kaggle competition"
```

**Features:**
- ✅ Interactive chat mode
- ✅ Model selection
- ✅ Scenario specification
- ✅ Configurable parameters (temperature, max tokens)
- ✅ Colored output
- ✅ Command help system
- ✅ Error handling

**Options:**
```
-m, --model MODEL     Specify model (default: rd-agent-data-science)
-s, --scenario NAME   Specify RD-Agent scenario
-t, --temperature N   Set temperature 0.0-2.0 (default: 0.7)
-n, --max-tokens N    Set max tokens (default: 1000)
-i, --interactive     Start interactive chat mode
-l, --list-models     List available models
-h, --help           Show help
```

### 2. `simple_chat.sh` - Quick and Easy Chat
**Lightweight script for quick interactions.**

```bash
# Interactive mode
./simple_chat.sh

# Single message
./simple_chat.sh "Your message here"
```

**Features:**
- ✅ Simple interface
- ✅ Interactive or single-message mode
- ✅ Automatic container status check
- ✅ Clear error messages

### 3. `chat_examples.sh` - Demonstration Examples
**Shows various usage patterns and example interactions.**

```bash
./chat_examples.sh
```

**Features:**
- ✅ Pre-built example queries
- ✅ Different model demonstrations
- ✅ Scenario usage examples
- ✅ Configuration guidance

### 4. `quick_docker_test.sh` - Container Validation
**Tests container functionality and API endpoints.**

```bash
./quick_docker_test.sh
```

**Features:**
- ✅ Container health check
- ✅ API endpoint validation
- ✅ Performance testing
- ✅ Comprehensive status report

## 🚀 Quick Start

### 1. Ensure Container is Running
```bash
# Check if container is running
docker ps --filter "name=rdagent-gateway-minimal"

# If not running, start it
docker-compose -f docker-compose.minimal.yml up -d
```

### 2. Test Basic Functionality
```bash
# Quick test
./quick_docker_test.sh

# Simple chat
./simple_chat.sh "Hello!"

# Interactive chat
./chat_interact.sh -i
```

### 3. Explore Examples
```bash
# See various example interactions
./chat_examples.sh
```

## 🎯 Available Models

| Model ID | Description | Best For |
|----------|-------------|----------|
| `rd-agent-data-science` | Data science and ML tasks | Kaggle competitions, ML pipelines |
| `rd-agent-quantitative-finance` | Financial modeling | Factor models, trading strategies |
| `rd-agent-general-model` | Research paper implementation | Academic research, general AI tasks |

## 📋 Example Usage Patterns

### Data Science Questions
```bash
./chat_interact.sh -m rd-agent-data-science \
  "How can I improve my machine learning model performance?"

./simple_chat.sh "Help me with feature engineering for a classification problem"
```

### Quantitative Finance
```bash
./chat_interact.sh -m rd-agent-quantitative-finance \
  "Explain the concept of factor models"

./simple_chat.sh "How do I build a multi-factor model for stock returns?"
```

### Research Papers
```bash
./chat_interact.sh -m rd-agent-general-model \
  "Help me understand this deep learning paper"
```

### Interactive Session
```bash
./chat_interact.sh -i
# Then type:
# > models (to switch models)
# > help (for commands)
# > clear (to clear screen)
# > exit (to quit)
```

## ⚙️ Configuration

### Current Container Settings
- **Base URL**: `http://localhost:8001`
- **Default Model**: `rd-agent-data-science`
- **Authentication**: Disabled (development mode)
- **CORS**: Enabled

### API Configuration (for full functionality)
Add these to your `.env` file:

```bash
# OpenAI API (required for LLM processing)
OPENAI_API_KEY=your-openai-api-key-here

# Kaggle API (for data science scenarios)
KAGGLE_USERNAME=your-kaggle-username
KAGGLE_KEY=your-kaggle-api-key

# Optional: DeepSeek API (alternative LLM)
CHAT_MODEL=deepseek/deepseek-chat
DEEPSEEK_API_KEY=your-deepseek-api-key
```

## 🔧 Troubleshooting

### Container Not Running
```bash
# Check container status
docker ps --filter "name=rdagent-gateway-minimal"

# Start container
docker-compose -f docker-compose.minimal.yml up -d

# Check logs
docker logs rdagent-gateway-minimal
```

### API Not Responding
```bash
# Test health endpoint
curl http://localhost:8001/health

# Check if port is available
netstat -tulpn | grep 8001
```

### Permission Issues
```bash
# Make scripts executable
chmod +x *.sh

# Or specifically
chmod +x chat_interact.sh simple_chat.sh chat_examples.sh quick_docker_test.sh
```

## 📊 Expected Responses

### With API Keys Configured
When properly configured with OpenAI/DeepSeek API keys, you'll receive:
```json
{
  "id": "chatcmpl-...",
  "object": "chat.completion",
  "created": 1234567890,
  "model": "rd-agent-data-science",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "I can help you with..."
    },
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 50,
    "total_tokens": 60
  }
}
```

### Without API Keys (Current State)
You'll see helpful error messages indicating what needs to be configured:
```
⚠️  Expected Response (API keys needed for full functionality):
   Error Type: internal_error

💡 To enable full functionality, configure:
   - KAGGLE_USERNAME and KAGGLE_KEY in .env file
   - OPENAI_API_KEY for LLM processing
```

## 🎨 Script Features

### User Experience
- **Colored output** for better readability
- **Interactive prompts** for ease of use
- **Error handling** with helpful messages
- **Status indicators** (✅❌⚠️💡)

### Technical Features
- **JSON payload construction** for API requests
- **Response parsing** with jq
- **Container status validation**
- **Multiple input modes** (interactive/single message)

## 📈 Performance Notes

- **Response times**: 2-5ms for basic endpoints
- **Container resources**: Minimal CPU/memory usage
- **Concurrent requests**: Handles multiple simultaneous connections
- **Error handling**: Robust error responses

## 🔗 Related Files

- `docker-compose.minimal.yml` - Container configuration
- `.env` - Environment variables
- `test_docker_container.py` - Python unit tests
- `docker-container-test-report.md` - Detailed test report

## 📝 Notes

1. **Development Mode**: Current setup is for development/testing
2. **API Keys**: Required for full RD-Agent functionality
3. **Scenarios**: Each model supports different scenario types
4. **OpenAI Compatibility**: Full compatibility with OpenAI client libraries

## 🎉 Getting Started Examples

```bash
# 1. Basic health check
./quick_docker_test.sh

# 2. Simple question
./simple_chat.sh "What is machine learning?"

# 3. Interactive session
./chat_interact.sh -i

# 4. Specific model query
./chat_interact.sh -m rd-agent-quantitative-finance "Explain alpha generation"

# 5. See all examples
./chat_examples.sh
```

**Happy Chatting with RD-Agent!** 🤖✨