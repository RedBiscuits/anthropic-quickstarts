# API Reference

Complete API documentation for the Computer Use Agent Backend.

## Table of Contents

- [Authentication](#authentication)
- [Base URL](#base-url)
- [Error Handling](#error-handling)
- [Endpoints](#endpoints)
- [WebSocket API](#websocket-api)
- [Data Models](#data-models)

## Authentication

Currently, the API doesn't require authentication. All endpoints are publicly accessible.

## Base URL

```
http://localhost:8000/api
```

## Error Handling

### Error Response Format

```json
{
  "detail": "Error message",
  "status_code": 400,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 404 | Not Found |
| 500 | Internal Server Error |

## Endpoints

### Health Check

#### GET `/api/health`

Check if the API is running.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T00:00:00Z",
  "version": "1.0.0"
}
```

### Sessions

#### POST `/api/sessions`

Create a new agent session.

**Request Body:**
```json
{
  "name": "Session Name"
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Session Name",
  "status": "active",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "message_count": 0
}
```

#### GET `/api/sessions`

Get all sessions.

**Response:**
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Session Name",
    "status": "active",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z",
    "message_count": 5
  }
]
```

#### GET `/api/sessions/{session_id}`

Get session details with messages.

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Session Name",
  "status": "active",
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z",
  "message_count": 5,
  "messages": [
    {
      "id": "msg-123",
      "session_id": "550e8400-e29b-41d4-a716-446655440000",
      "role": "user",
      "content": "Hello",
      "timestamp": "2024-01-01T00:00:00Z",
      "message_metadata": {},
      "tool_executions": []
    }
  ]
}
```

#### DELETE `/api/sessions/{session_id}`

Delete a session.

**Response:**
```json
{
  "message": "Session 550e8400-e29b-41d4-a716-446655440000 deleted successfully"
}
```

### Messages

#### POST `/api/sessions/{session_id}/messages`

Send a message to an agent session.

**Request Body:**
```json
{
  "content": "Message content"
}
```

**Response:**
```json
{
  "id": "processing",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "role": "user",
  "content": "Message content",
  "timestamp": "2024-01-01T00:00:00Z",
  "message_metadata": {
    "status": "processing"
  },
  "tool_executions": []
}
```

#### GET `/api/sessions/{session_id}/messages`

Get all messages for a session.

**Response:**
```json
[
  {
    "id": "msg-123",
    "session_id": "550e8400-e29b-41d4-a716-446655440000",
    "role": "user",
    "content": "Hello",
    "timestamp": "2024-01-01T00:00:00Z",
    "message_metadata": {},
    "tool_executions": []
  }
]
```

## WebSocket API

### Connection

```
ws://localhost:8000/api/ws/{session_id}
```

### Message Types

#### Connection Message
```json
{
  "type": "connection",
  "data": {
    "message": "Connected to session",
    "session_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

#### Agent Progress Message
```json
{
  "type": "agent_progress",
  "data": {
    "message": "Processing your request...",
    "step": "thinking",
    "progress": 0.25
  }
}
```

#### Tool Execution Message
```json
{
  "type": "tool_execution",
  "data": {
    "tool_name": "computer",
    "tool_input": {
      "action": "click",
      "coordinate": [100, 200]
    },
    "tool_output": {
      "status": "completed",
      "result": "Clicked at position (100, 200)"
    },
    "status": "completed"
  }
}
```

#### Agent Response Message
```json
{
  "type": "agent_response",
  "data": {
    "content": "I found the weather information...",
    "message_id": "msg-124"
  }
}
```

#### Error Message
```json
{
  "type": "error",
  "data": {
    "message": "Failed to process request",
    "error_code": "API_ERROR"
  }
}
```

## Data Models

### Session

```json
{
  "id": "string (UUID)",
  "name": "string",
  "status": "active | completed | error | cancelled",
  "created_at": "datetime",
  "updated_at": "datetime",
  "message_count": "integer"
}
```

### Message

```json
{
  "id": "string (UUID)",
  "session_id": "string (UUID)",
  "role": "user | assistant | system",
  "content": "string",
  "timestamp": "datetime",
  "message_metadata": "object",
  "tool_executions": "array"
}
```

### Tool Execution

```json
{
  "id": "string (UUID)",
  "message_id": "string (UUID)",
  "tool_name": "string",
  "tool_input": "object",
  "tool_output": "object",
  "execution_time": "float",
  "status": "running | completed | error",
  "created_at": "datetime",
  "completed_at": "datetime"
}
```

```

```markdown:anthropic-quickstarts/computer-use-backend/DEPLOYMENT.md
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