# Deployment Guide

Complete guide for deploying the Computer Use Agent Backend to production.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Production Setup](#production-setup)
- [Docker Deployment](#docker-deployment)
- [Environment Configuration](#environment-configuration)
- [Security Considerations](#security-considerations)
- [Monitoring](#monitoring)
- [Scaling](#scaling)
- [Backup & Recovery](#backup--recovery)

## Prerequisites

- Docker and Docker Compose
- Domain name (optional)
- SSL certificate (recommended)
- Monitoring tools
- Backup solution

## Production Setup

### 1. Environment Configuration

Create production environment file:

```bash
# .env.prod
ANTHROPIC_API_KEY=your_production_api_key
API_PROVIDER=anthropic
MODEL_NAME=claude-sonnet-4-20250514
DATABASE_URL=sqlite:///data/computer_use.db
WIDTH=1024
HEIGHT=768
LOG_LEVEL=INFO
CORS_ORIGINS=https://yourdomain.com
```

### 2. Production Docker Compose

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  backend:
    build: .
    container_name: computer-use-backend-prod
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - DATABASE_URL=${DATABASE_URL}
      - API_PROVIDER=${API_PROVIDER}
      - MODEL_NAME=${MODEL_NAME}
      - LOG_LEVEL=${LOG_LEVEL}
      - CORS_ORIGINS=${CORS_ORIGINS}
    volumes:
      - ./data:/app/data
      - ./frontend:/app/frontend
      - ./logs:/app/logs
    depends_on:
      - agent-container
    networks:
      - computer-use-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

  agent-container:
    image: ghcr.io/anthropics/anthropic-quickstarts:computer-use-demo-latest
    container_name: computer-use-agent-prod
    restart: unless-stopped
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - API_PROVIDER=${API_PROVIDER}
      - MODEL_NAME=${MODEL_NAME}
      - DISPLAY=:1
      - WIDTH=${WIDTH}
      - HEIGHT=${HEIGHT}
    ports:
      - "5900:5900"
      - "6080:6080"
      - "8080:8080"
    volumes:
      - agent-data:/home/computeruse/.anthropic
    networks:
      - computer-use-network
    stdin_open: true
    tty: true
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

  nginx:
    image: nginx:alpine
    container_name: computer-use-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend
    networks:
      - computer-use-network

networks:
  computer-use-network:
    driver: bridge

volumes:
  agent-data:
    driver: local
```

### 3. Nginx Configuration

```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    server {
        listen 80;
        server_name yourdomain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl;
        server_name yourdomain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        location / {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /ws/ {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

## Docker Deployment

### 1. Build and Deploy

```bash
# Build production images
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# Deploy to production
docker-compose -f docker-compose.yml -f doc 