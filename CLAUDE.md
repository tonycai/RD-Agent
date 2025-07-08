# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

R&D-Agent is a comprehensive framework for automating data-driven research and development processes. It's built around the concept of "R" (Research - proposing ideas) and "D" (Development - implementing them) with a focus on machine learning, quantitative finance, and data science applications.

## Core Architecture

The project follows a modular architecture with these key components:

### Core Framework (`rdagent/core/`)
- **Scenario**: Abstract base class for different R&D scenarios
- **Evolving Framework**: Orchestrates the evolution of solutions through iterative feedback
- **Experiment**: Manages experiment lifecycle and execution
- **Proposal**: Handles idea generation and refinement
- **Evaluation**: Provides feedback mechanisms for iterative improvement

### Application Scenarios (`rdagent/scenarios/`)
- **Data Science**: Kaggle-style competitions and ML pipelines
- **Quantitative Finance**: Factor discovery and model optimization
- **General Model**: Research paper implementation

### Components (`rdagent/components/`)
- **Coder**: Various specialized coders (CoSTEER framework) for different tasks
- **Runner**: Execution environments for different scenarios
- **Workflow**: R&D loop orchestration and management

## Common Development Commands

### Setup and Installation
```bash
# Install in development mode with all dependencies
make dev

# Install specific optional dependencies
make dev-docs  # for documentation
make dev-test  # for testing
make dev-lint  # for linting tools

# Health check to verify setup
rdagent health_check
```

### Linting and Code Quality
```bash
# Run all linters
make lint

# Individual linters
make mypy     # Type checking (focused on rdagent/core)
make ruff     # Code style and quality
make black    # Code formatting check
make isort    # Import sorting check
make toml-sort # TOML file formatting

# Auto-fix linting issues
make auto-lint  # Fixes isort, black, and toml-sort issues
```

### Testing
```bash
# Run full test suite with coverage
make test

# Run offline tests only (no API calls)
make test-offline

# Run tests without coverage reporting
make test-run
```

### Documentation
```bash
# Generate documentation with auto-reload
make docs-autobuild

# Generate static documentation
make docs-gen

# Generate full docs with reports
make docs
```

### Application Entry Points
```bash
# CLI commands via rdagent:
rdagent data_science --competition <competition_name>  # Kaggle scenarios
rdagent fin_quant      # Quantitative finance with joint factor-model optimization
rdagent fin_factor     # Factor discovery and evolution
rdagent fin_model      # Model evolution for quant finance
rdagent general_model <paper_url>  # Research paper implementation
rdagent ui --port 19899 --log_dir <log_dir>  # Web UI for monitoring

# OpenAI-compatible Gateway API server
uvicorn rdagent.app.gateway.main_new:app --host 0.0.0.0 --port 8000

# Legacy Gateway API server
uvicorn rdagent.app.gateway.main:app --host 0.0.0.0 --port 8000
```

## Key Development Patterns

### Scenario Implementation
All scenarios inherit from `rdagent.core.scenario.Scenario` and must implement:
- `background`: Scenario description
- `get_source_data_desc()`: Data description
- `rich_style_description`: UI presentation format
- `get_scenario_all_desc()`: Complete scenario context

### CoSTEER Framework
The Collaborative Evolving Strategy for Automatic Data-Centric Development:
- **Coder**: Implements solutions for specific tasks
- **Runner**: Executes and evaluates implementations
- **Feedback**: Provides iterative improvement signals

### Experiment Lifecycle
1. **Proposal Generation**: Ideas are generated based on current knowledge
2. **Implementation**: Coders convert ideas into executable code
3. **Execution**: Runners execute the implementation
4. **Feedback**: Results are analyzed and fed back for improvement
5. **Evolution**: Knowledge base is updated for future iterations

## Configuration

### Environment Variables
The project uses `.env` files for configuration:
- `CHAT_MODEL`: Primary LLM model (e.g., gpt-4o, deepseek/deepseek-chat)
- `EMBEDDING_MODEL`: Embedding model for vector operations
- `OPENAI_API_KEY`: API key for OpenAI models
- `DEEPSEEK_API_KEY`: API key for DeepSeek models
- `REASONING_THINK_RM=True`: For reasoning models with thought processes

### LiteLLM Backend
The project supports LiteLLM for multiple LLM providers with flexible configuration options.

## Docker Requirements
Most scenarios require Docker for isolated execution environments. Ensure Docker is installed and the current user can run Docker commands without sudo.

## Package Structure
- `rdagent/app/`: Application entry points for different scenarios
- `rdagent/components/`: Reusable components (coders, runners, evaluators)
- `rdagent/core/`: Core framework abstractions
- `rdagent/scenarios/`: Specific scenario implementations
- `rdagent/utils/`: Utility functions and helpers
- `rdagent/log/`: Logging and monitoring infrastructure
- `rdagent/oai/`: LLM backend abstraction layer

## Testing Strategy
- Unit tests focus on core functionality
- Integration tests verify scenario workflows
- Coverage threshold is currently set to 20% (being gradually increased)
- Offline tests can run without API access for faster CI/CD

### Running Individual Tests
```bash
# Run a specific test file
pytest test/utils/test_misc.py

# Run tests with specific markers
pytest -m "offline"

# Run tests with verbose output
pytest -v test/utils/test_misc.py
```

## Development Workflow Patterns

### Coder-Runner-Feedback Loop
The project implements a sophisticated CoSTEER (Collaborative Evolving Strategy for Automatic Data-Centric Development) framework:

1. **Coder Components** (`rdagent/components/coder/`):
   - `CoSTEER/`: Core evolving strategy framework
   - `data_science/`: ML pipeline coders (feature, model, ensemble)
   - `factor_coder/`: Financial factor generation
   - `model_coder/`: Model structure implementation

2. **Runner Components** (`rdagent/components/runner/`):
   - Execute generated code in isolated environments
   - Provide feedback for iterative improvement

3. **Feedback Loop** (`rdagent/core/evaluation.py`):
   - Analyzes execution results
   - Generates improvement suggestions
   - Feeds back into next iteration

### Scenario Architecture
All scenarios follow a consistent pattern inheriting from `rdagent.core.scenario.Scenario`:

```python
# Key methods to implement:
background: str                    # Scenario description
get_source_data_desc()            # Data description
rich_style_description            # UI presentation
get_scenario_all_desc()           # Complete context
```

### Key Configuration Files
- `.env`: Environment variables for API keys and model configuration
- `rdagent/core/conf.py`: Core configuration constants
- `rdagent/oai/llm_conf.py`: LLM backend configuration
- Individual scenario configs in `rdagent/scenarios/*/conf.py`

## Debugging and Troubleshooting

### Common Issues
1. **Docker permissions**: Ensure user can run `docker run hello-world` without sudo
2. **API rate limits**: Configure appropriate retry logic in `.env`
3. **Model context limits**: Large codebases may exceed token limits

### Debugging Commands
```bash
# Check system health
rdagent health_check

# Debug specific scenario with verbose logging
rdagent data_science --competition sf-crime --verbose

# View execution logs
rdagent ui --port 19899 --log_dir log/
```

## File Generation Patterns

### Template-based Generation
The project uses extensive template-based code generation:
- `rdagent/scenarios/kaggle/experiment/templates/`: Competition-specific templates
- `rdagent/components/coder/*/prompts.yaml`: Prompt templates for different coders
- Template inheritance and customization for different scenarios

### Knowledge Management
- `rdagent/components/knowledge_management/`: Vector-based knowledge storage
- `rdagent/log/`: Comprehensive logging and trace storage
- Iterative learning from previous experiment results

## OpenAI-Compatible Gateway

The project includes a comprehensive OpenAI-compatible RESTful API gateway that enables seamless integration with existing tools and frameworks.

### Gateway Architecture
```
rdagent/app/gateway/
├── main_new.py           # OpenAI-compatible FastAPI application
├── main.py               # Legacy implementation  
├── schema.py             # Complete OpenAI API schemas
├── auth.py               # Bearer token authentication
├── settings.py           # Configuration management
├── exceptions.py         # Error handling
├── models/
│   ├── base.py          # Model abstraction layer
│   └── rd_agent.py      # RD-Agent implementation
├── routers/
│   ├── chat.py          # Chat completions endpoint
│   ├── models.py        # Model listing
│   └── health.py        # Health checks
└── examples/            # Usage examples and configs
```

### Key Gateway Features
- **Full OpenAI API Compatibility**: Compatible with OpenAI client libraries
- **Multiple Scenarios**: Support for data science, quantitative finance, and general model scenarios
- **Streaming Support**: Server-sent events (SSE) for real-time responses
- **Authentication**: Optional bearer token authentication with multiple sources
- **Error Handling**: Comprehensive OpenAI-compatible error responses
- **Model Management**: Dynamic model discovery and registration
- **Request Validation**: Comprehensive input validation with detailed error messages

### Gateway Configuration
```bash
# Environment variables for gateway configuration
RD_AGENT_HOST=0.0.0.0
RD_AGENT_PORT=8000
RD_AGENT_AUTH_ENABLED=true
RD_AGENT_API_KEY=your-api-key
RD_AGENT_DEFAULT_SCENARIO=data_science
RD_AGENT_MAX_STEPS=10
```

### Usage Examples
```bash
# List available models
curl http://localhost:8000/v1/models

# Chat completion with RD-Agent extensions
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "rd-agent-data-science",
    "messages": [{"role": "user", "content": "Start sf-crime competition"}],
    "stream": true,
    "rd_agent": {
      "competition": "sf-crime",
      "steps": 3
    }
  }'
```

### Available Models
- `rd-agent-data-science`: Data science and Kaggle competitions
- `rd-agent-quantitative-finance`: Factor and model optimization  
- `rd-agent-general-model`: Research paper implementation

### Integration Examples
```python
# Using OpenAI Python client
from openai import OpenAI

client = OpenAI(
    api_key="your-api-key",
    base_url="http://localhost:8000/v1"
)

response = client.chat.completions.create(
    model="rd-agent-data-science",
    messages=[{"role": "user", "content": "Start data science project"}],
    extra_body={"rd_agent": {"competition": "sf-crime", "steps": 3}}
)
```

## Docker Deployment

The project includes comprehensive Docker support for easy deployment and scaling.

### Docker Architecture
```
├── Dockerfile                    # Multi-stage Docker build (dev/prod/gateway)
├── docker-compose.yml           # Main compose configuration
├── docker-compose.dev.yml       # Development overrides
├── docker-compose.prod.yml      # Production optimizations
├── docker-compose.minimal.yml   # Lightweight gateway-only setup
├── .env.docker                  # Environment template
├── Makefile.docker             # Automation commands
└── docker/
    ├── entrypoint.sh           # Container entrypoint script
    ├── nginx/                  # Reverse proxy configuration
    ├── prometheus/             # Monitoring setup
    └── litellm/               # LLM proxy configuration
```

### Quick Start with Docker
```bash
# Clone and setup
git clone https://github.com/microsoft/RD-Agent.git
cd RD-Agent

# Quick development start
make -f Makefile.docker quick-start

# Or minimal gateway only
docker-compose -f docker-compose.minimal.yml up -d

# Check status
curl http://localhost:8000/health
```

### Docker Deployment Options

#### 1. Minimal (Gateway Only)
```bash
docker-compose -f docker-compose.minimal.yml up -d
```
- ✅ OpenAI-compatible API gateway
- ✅ Health checks
- 🚀 Fastest startup, minimal resources

#### 2. Development Environment
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```
- ✅ Gateway with hot reload
- ✅ UI monitoring dashboard
- ✅ Redis caching
- ✅ Nginx reverse proxy
- ✅ PostgreSQL database

#### 3. Production Environment
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```
- ✅ Optimized gateway (multiple replicas)
- ✅ Production database with backups
- ✅ SSL-ready Nginx configuration
- ✅ Resource limits and health checks

#### 4. Full Stack with Monitoring
```bash
docker-compose --profile monitoring up -d
```
- ✅ All production features
- ✅ Prometheus metrics collection
- ✅ Grafana dashboards
- ✅ Service monitoring and alerting

### Docker Services and Ports

| Service | Port | Description |
|---------|------|-------------|
| Gateway | 8000 | OpenAI-compatible API |
| UI | 19899 | Monitoring dashboard |
| Nginx | 80/443 | Reverse proxy |
| Redis | 6379 | Caching layer |
| PostgreSQL | 5432 | Database |
| Prometheus | 9090 | Metrics collection |
| Grafana | 3000 | Monitoring dashboards |
| LiteLLM | 4000 | LLM aggregation proxy |

### Docker Commands Reference
```bash
# Build and start
make -f Makefile.docker docker-build
make -f Makefile.docker docker-up-dev

# Monitoring
make -f Makefile.docker docker-health
make -f Makefile.docker docker-logs

# Shell access
make -f Makefile.docker docker-shell

# Cleanup
make -f Makefile.docker docker-clean

# Testing
make -f Makefile.docker docker-test
```

### Environment Configuration
Create `.env` from template:
```bash
cp .env.docker .env
# Edit with your API keys and settings

# Key variables:
RD_AGENT_AUTH_ENABLED=false
RD_AGENT_API_KEY=your-secure-key
OPENAI_API_KEY=your-openai-key
CHAT_MODEL=gpt-4o
EMBEDDING_MODEL=text-embedding-3-small
```

### Production Deployment Checklist
- [ ] Configure SSL certificates in Nginx
- [ ] Enable authentication (`RD_AGENT_AUTH_ENABLED=true`)
- [ ] Set secure API keys
- [ ] Configure backup strategy
- [ ] Set up monitoring alerts
- [ ] Configure log rotation
- [ ] Test disaster recovery

For complete Docker deployment instructions, see `DOCKER.md`.