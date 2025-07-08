# Multi-stage Dockerfile for RD-Agent with OpenAI-compatible Gateway
FROM python:3.11-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    wget \
    unzip \
    vim \
    htop \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Install Docker CLI (for RD-Agent Docker execution)
RUN curl -fsSL https://get.docker.com -o get-docker.sh && \
    sh get-docker.sh && \
    rm get-docker.sh

# Create app user
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid appuser --shell /bin/bash --create-home appuser

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
COPY requirements/ requirements/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Development stage
FROM base as development

# Install development dependencies
RUN pip install --no-cache-dir -r requirements/docs.txt && \
    pip install --no-cache-dir -r requirements/lint.txt && \
    pip install --no-cache-dir -r requirements/test.txt

# Copy the entire project
COPY . .

# Install the package in development mode
RUN pip install -e .

# Change ownership to appuser
RUN chown -R appuser:appuser /app

USER appuser

# Expose ports
EXPOSE 8000 19899

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["uvicorn", "rdagent.app.gateway.main_new:app", "--host", "0.0.0.0", "--port", "8000"]

# Production stage
FROM base as production

# Copy only necessary files
COPY rdagent/ rdagent/
COPY pyproject.toml .
COPY README.md .
COPY LICENSE .

# Set version for setuptools-scm
ENV SETUPTOOLS_SCM_PRETEND_VERSION_FOR_RDAGENT=0.1.0

# Install the package
RUN pip install --no-cache-dir .

# Change ownership to appuser
RUN chown -R appuser:appuser /app

USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["uvicorn", "rdagent.app.gateway.main_new:app", "--host", "0.0.0.0", "--port", "8000"]

# Gateway-only stage (lightweight)
FROM python:3.11-slim as gateway

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install minimal system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid appuser --shell /bin/bash --create-home appuser

WORKDIR /app

# Install minimal Python dependencies for gateway only
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn[standard] \
    pydantic \
    pydantic-settings \
    python-dotenv \
    loguru

# Copy only gateway-related files
COPY rdagent/app/gateway/ rdagent/app/gateway/
COPY rdagent/__init__.py rdagent/
COPY rdagent/app/__init__.py rdagent/app/

# Create minimal __init__.py files
RUN touch rdagent/app/gateway/__init__.py

# Change ownership to appuser
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command
CMD ["uvicorn", "rdagent.app.gateway.main_new:app", "--host", "0.0.0.0", "--port", "8000"]