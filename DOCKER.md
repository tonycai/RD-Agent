# 🐳 RD-Agent Docker Deployment Guide

This guide provides comprehensive instructions for deploying RD-Agent using Docker and Docker Compose.

## 📋 Prerequisites

- Docker Engine 20.10+ 
- Docker Compose 2.0+
- At least 4GB RAM available
- 10GB+ disk space
- (Optional) NVIDIA Docker for GPU support

### Quick Installation Check

```bash
# Check Docker version
docker --version

# Check Docker Compose version  
docker-compose --version

# Verify Docker is running
docker run hello-world
```

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/microsoft/RD-Agent.git
cd RD-Agent

# Setup environment file
cp .env.docker .env

# Edit environment variables
vim .env
```

### 2. Minimal Deployment (Gateway Only)

```bash
# Start minimal setup (fastest)
docker-compose -f docker-compose.minimal.yml up -d

# Check status
curl http://localhost:8000/health
```

### 3. Development Environment

```bash
# Start full development environment
make -f Makefile.docker quick-start

# Or manually:
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

### 4. Production Environment  

```bash
# Configure production environment
cp .env.docker .env
# Edit .env with production settings

# Start production stack
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 📁 Project Structure

```
RD-Agent/
├── Dockerfile                    # Multi-stage Dockerfile
├── docker-compose.yml           # Main compose file
├── docker-compose.dev.yml       # Development overrides
├── docker-compose.prod.yml      # Production overrides  
├── docker-compose.minimal.yml   # Minimal setup
├── .env.docker                  # Environment template
├── Makefile.docker             # Docker automation
└── docker/                     # Docker configurations
    ├── entrypoint.sh           # Container entrypoint
    ├── nginx/                  # Nginx configuration
    ├── prometheus/             # Monitoring config
    └── litellm/               # LiteLLM proxy config
```

## 🔧 Configuration

### Environment Variables

Key environment variables in `.env`:

```bash
# Authentication
RD_AGENT_AUTH_ENABLED=false
RD_AGENT_API_KEY=your-secure-api-key

# LLM Configuration
OPENAI_API_KEY=your-openai-key
CHAT_MODEL=gpt-4o
EMBEDDING_MODEL=text-embedding-3-small

# DeepSeek (Alternative)
DEEPSEEK_API_KEY=your-deepseek-key
CHAT_MODEL=deepseek/deepseek-chat

# Monitoring
GRAFANA_PASSWORD=admin
```

### Service Ports

| Service | Port | Description |
|---------|------|-------------|
| Gateway | 8000 | OpenAI-compatible API |
| UI | 19899 | Monitoring dashboard |
| Nginx | 80/443 | Reverse proxy |
| Redis | 6379 | Caching |
| Grafana | 3000 | Monitoring |
| Prometheus | 9090 | Metrics |
| LiteLLM | 4000 | LLM proxy |

## 🏗️ Deployment Options

### 1. Minimal (Gateway Only)

Fastest startup, minimal resources:

```bash
docker-compose -f docker-compose.minimal.yml up -d
```

**Includes:**
- ✅ RD-Agent Gateway (OpenAI API)
- ✅ Health checks
- ❌ UI, monitoring, proxy

### 2. Development Environment

Full features with hot reload:

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

**Includes:**
- ✅ Gateway with hot reload
- ✅ UI dashboard  
- ✅ Redis caching
- ✅ Nginx proxy
- ✅ PostgreSQL database
- ❌ Monitoring stack

### 3. Production Environment

Production-ready with monitoring:

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

**Includes:**
- ✅ Optimized gateway (2 replicas)
- ✅ UI dashboard
- ✅ Redis caching
- ✅ Nginx with SSL support
- ✅ PostgreSQL with backups
- ✅ Resource limits

### 4. Full Stack with Monitoring

Complete setup with metrics:

```bash
docker-compose --profile monitoring up -d
```

**Includes:**
- ✅ All production features
- ✅ Prometheus metrics
- ✅ Grafana dashboards
- ✅ Health monitoring

### 5. With LiteLLM Proxy

Add LLM aggregation layer:

```bash
docker-compose --profile litellm up -d
```

**Includes:**
- ✅ LiteLLM proxy for multiple LLM providers
- ✅ Load balancing across LLMs
- ✅ Request routing and caching

## 🛠️ Make Commands

Use the provided Makefile for common operations:

```bash
# Quick start development environment
make -f Makefile.docker quick-start

# Build all images
make -f Makefile.docker docker-build

# Start services
make -f Makefile.docker docker-up-dev      # Development
make -f Makefile.docker docker-up-prod     # Production  
make -f Makefile.docker docker-up-minimal  # Minimal

# View logs
make -f Makefile.docker docker-logs
make -f Makefile.docker docker-logs-gateway

# Health check
make -f Makefile.docker docker-health

# Shell access
make -f Makefile.docker docker-shell

# Clean up
make -f Makefile.docker docker-clean
```

## 🔍 Monitoring and Logging

### Health Checks

```bash
# Check all services
make -f Makefile.docker docker-health

# Individual health checks
curl http://localhost:8000/health          # Gateway
curl http://localhost:19899                # UI  
curl http://localhost:9090/-/healthy       # Prometheus
```

### Viewing Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f rdagent-gateway
docker-compose logs -f rdagent-ui

# With Make
make -f Makefile.docker docker-logs
make -f Makefile.docker docker-logs-gateway
```

### Monitoring Stack

When using the monitoring profile:

- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Metrics endpoint**: http://localhost:8000/metrics

## 🧪 Testing

### Running Tests in Container

```bash
# Run all tests
make -f Makefile.docker docker-test

# Run offline tests only
make -f Makefile.docker docker-test-offline

# Manual testing
docker-compose exec rdagent-gateway python -m pytest
```

### API Testing

```bash
# List models
curl http://localhost:8000/v1/models

# Chat completion
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "rd-agent-data-science",
    "messages": [{"role": "user", "content": "Hello"}],
    "stream": false
  }'
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Port Already in Use

```bash
# Check what's using the port
sudo lsof -i :8000

# Kill the process
sudo kill -9 <PID>

# Or change port in .env
RD_AGENT_PORT=8001
```

#### 2. Docker Permission Denied

```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Logout and login again, or:
newgrp docker
```

#### 3. Out of Memory

```bash
# Check Docker memory
docker system df

# Clean up unused resources
docker system prune -f
make -f Makefile.docker docker-clean
```

#### 4. API Keys Not Working

```bash
# Check environment variables
docker-compose exec rdagent-gateway env | grep API_KEY

# Verify .env file
cat .env | grep API_KEY
```

#### 5. Container Won't Start

```bash
# Check container logs
docker-compose logs rdagent-gateway

# Check resource usage
docker stats

# Restart specific service
docker-compose restart rdagent-gateway
```

### Debug Mode

Enable debug logging:

```bash
# In .env file
RD_AGENT_DEBUG=true
RD_AGENT_LOG_LEVEL=DEBUG

# Restart services
docker-compose restart
```

### Container Shell Access

```bash
# Gateway container
make -f Makefile.docker docker-shell

# Or manually
docker-compose exec rdagent-gateway /bin/bash

# Check processes
docker-compose exec rdagent-gateway ps aux

# Check file system
docker-compose exec rdagent-gateway ls -la /app
```

## 🔒 Security

### Production Security Checklist

- [ ] Enable authentication (`RD_AGENT_AUTH_ENABLED=true`)
- [ ] Set strong API keys (`RD_AGENT_API_KEY`)
- [ ] Configure SSL certificates in Nginx
- [ ] Restrict CORS origins (`RD_AGENT_CORS_ORIGINS`)
- [ ] Enable rate limiting
- [ ] Use secrets management for sensitive data
- [ ] Regularly update base images
- [ ] Monitor for security vulnerabilities

### SSL Configuration

For production with SSL:

1. Obtain SSL certificates
2. Mount certificates in Nginx container
3. Update `docker/nginx/default.conf` with SSL config
4. Use production docker-compose file

```bash
# Example SSL setup
volumes:
  - ./certs/yourdomain.com.crt:/etc/ssl/certs/yourdomain.com.crt:ro
  - ./certs/yourdomain.com.key:/etc/ssl/private/yourdomain.com.key:ro
```

## 🚀 Production Deployment

### 1. Server Requirements

**Minimum:**
- 2 CPU cores
- 4GB RAM  
- 20GB storage
- Ubuntu 20.04+ or CentOS 8+

**Recommended:**
- 4+ CPU cores
- 8GB+ RAM
- 50GB+ SSD storage
- Load balancer (for multiple instances)

### 2. Production Checklist

- [ ] Configure environment variables
- [ ] Set up SSL certificates  
- [ ] Configure backup strategy
- [ ] Set up monitoring alerts
- [ ] Configure log rotation
- [ ] Test disaster recovery
- [ ] Document deployment process

### 3. Scaling

#### Horizontal Scaling

```yaml
# In docker-compose.prod.yml
rdagent-gateway:
  deploy:
    replicas: 3
```

#### Database Scaling

```yaml
# Add read replicas
postgres-read:
  image: postgres:15-alpine
  environment:
    - POSTGRES_MASTER_HOST=postgres
```

#### Load Balancing

Configure Nginx for multiple gateway instances:

```nginx
upstream rdagent_gateway {
    server rdagent-gateway-1:8000;
    server rdagent-gateway-2:8000;
    server rdagent-gateway-3:8000;
}
```

## 📊 Performance Tuning

### Gateway Performance

```yaml
# Increase workers for production
environment:
  - WORKERS=4
  - WORKER_CLASS=uvicorn.workers.UvicornWorker
```

### Database Performance

```yaml
# PostgreSQL tuning
environment:
  - POSTGRES_SHARED_BUFFERS=256MB
  - POSTGRES_EFFECTIVE_CACHE_SIZE=1GB
  - POSTGRES_MAX_CONNECTIONS=200
```

### Resource Limits

```yaml
# Set resource limits
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 4G
    reservations:
      cpus: '1.0'  
      memory: 2G
```

## 🔄 Updates and Maintenance

### Updating Services

```bash
# Pull latest images
docker-compose pull

# Recreate containers with new images
docker-compose up -d

# Or with Make
make -f Makefile.docker docker-update
```

### Backup Strategy

```bash
# Database backup
make -f Makefile.docker docker-backup

# Volume backup
docker run --rm -v rdagent_postgres-data:/data -v $(pwd):/backup ubuntu tar czf /backup/postgres-backup.tar.gz /data
```

### Log Rotation

Configure log rotation in production:

```yaml
# In docker-compose.prod.yml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

## 🆘 Support

### Getting Help

1. Check logs: `make -f Makefile.docker docker-logs`
2. Verify health: `make -f Makefile.docker docker-health`  
3. Check documentation: `docker-compose exec rdagent-gateway rdagent --help`
4. Create GitHub issue: https://github.com/microsoft/RD-Agent/issues

### Useful Commands

```bash
# View all containers
docker ps -a

# View resource usage
docker stats

# Clean up everything
make -f Makefile.docker docker-clean

# Reset everything  
make -f Makefile.docker docker-reset

# View Docker system info
docker system info
```

This completes the comprehensive Docker deployment guide for RD-Agent! 🎉