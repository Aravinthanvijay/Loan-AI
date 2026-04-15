# Docker Setup Guide

This project can be containerized and run using Docker and Docker Compose for easy deployment.

## Prerequisites

- Docker (20.10+)
- Docker Compose (2.0+)
- Environment variables configured

## Quick Start

### 1. Configure Environment

Copy the example environment file and set your values:

```bash
cp .env.example .env
```

Edit `.env` and set:
- `GROQ_API_KEY`: Your Groq API key
- `MONGODB_PASSWORD`: Strong MongoDB password (change from default)
- `JWT_SECRET_KEY`: Strong JWT secret (change from default)

### 2. Build Images

Build all service images:

```bash
docker-compose build
```

Build specific service:

```bash
docker-compose build backend
docker-compose build frontend
```

### 3. Start Services

Start all services:

```bash
docker-compose up -d
```

View logs:

```bash
docker-compose logs -f
```

View specific service logs:

```bash
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f mongodb
```

### 4. Access Services

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **MongoDB**: mongodb://admin:password@localhost:27017/loan_ai

### 5. Stop Services

Stop all services:

```bash
docker-compose down
```

Stop and remove volumes (careful - deletes data):

```bash
docker-compose down -v
```

## Services Overview

### MongoDB
- **Image**: mongo:7.0-alpine
- **Port**: 27017
- **Volume**: mongodb_data (persistent)
- **Health Check**: Enabled
- **Default User**: admin

### Backend
- **Image**: Built from `backend/Dockerfile`
- **Port**: 8000
- **Framework**: FastAPI
- **Dependencies**: MongoDB, Groq API
- **Health Check**: Enabled
- **Volumes**: 
  - `backend_uploads`: Document uploads
  - `backend_logs`: Application logs

### Frontend
- **Image**: Built from `frontend/Dockerfile`
- **Port**: 3000
- **Framework**: React + Vite
- **Server**: `serve`
- **Health Check**: Enabled

## Docker Commands

### View Running Containers

```bash
docker-compose ps
```

### Execute Command in Container

```bash
docker-compose exec backend bash
docker-compose exec frontend sh
docker-compose exec mongodb mongosh
```

### View Container Resource Usage

```bash
docker stats
```

### Rebuild Cache-Free

```bash
docker-compose build --no-cache
```

### Pull Latest Images

```bash
docker-compose pull
```

## Volumes

### Database Volume
- **Name**: `mongodb_data`
- **Purpose**: MongoDB data persistence
- **Location**: Docker managed

### Backend Volumes
- **backend_uploads**: User document uploads
- **backend_logs**: Application logs

### View Volumes

```bash
docker volume ls
docker volume inspect loan_ai_mongodb_data
```

### Backup MongoDB Data

```bash
docker-compose exec mongodb mongodump --out /backup
docker cp loan_ai_mongodb:/backup ./backup
```

### Restore MongoDB Data

```bash
docker cp ./backup loan_ai_mongodb:/restore
docker-compose exec mongodb mongorestore /restore
```

## Networking

Services communicate via internal Docker network `loan_ai_network`:

- Backend to MongoDB: `mongodb://admin:password@mongodb:27017/loan_ai`
- Frontend to Backend: `http://backend:8000/api`

## Health Checks

Each service has a health check endpoint:

```bash
# Check status
docker-compose ps

# View health details
docker inspect loan_ai_backend
```

## Troubleshooting

### Port Already in Use

If ports 3000, 8000, or 27017 are in use:

```bash
# Change ports in docker-compose.yml
ports:
  - "3001:3000"  # frontend
  - "8001:8000"  # backend
  - "27018:27017"  # mongodb
```

Then update `VITE_API_URL` in `.env`:
```
VITE_API_URL=http://localhost:8001/api
```

### MongoDB Connection Issues

```bash
# Check MongoDB logs
docker-compose logs mongodb

# Test connection
docker-compose exec mongodb mongosh -u admin -p password
```

### Backend Not Starting

```bash
# Check backend logs
docker-compose logs backend

# Verify environment variables
docker-compose exec backend env | grep GROQ
```

### Frontend Not Loading

```bash
# Check frontend logs
docker-compose logs frontend

# Verify API URL in container
docker-compose exec frontend cat dist/index.html
```

### Rebuild Due to Changes

After code changes:

```bash
# Rebuild affected service
docker-compose build backend
docker-compose up -d backend

# Or restart service
docker-compose restart backend
```

## Performance Tuning

### Increase Timeout

If services are timing out on startup:

```yaml
# docker-compose.yml
services:
  backend:
    healthcheck:
      start_period: 30s  # Increase from 10s
```

### Memory Limits

Add resource limits to docker-compose.yml:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
        reservations:
          cpus: '0.5'
          memory: 512M
```

### MongoDB Performance

For production, add indexes and tune:

```bash
docker-compose exec mongodb mongosh
db.applications.createIndex({ "userId": 1 })
db.applications.createIndex({ "status": 1 })
```

## Production Deployment

### Security Checklist

- [ ] Change default MongoDB password
- [ ] Set strong JWT secret key
- [ ] Set valid Groq API key
- [ ] Use `.env` file not checked into git
- [ ] Enable HTTPS/SSL
- [ ] Set resource limits

### Production Example

```bash
# Build for production
docker-compose -f docker-compose.yml build

# Start with restart policy
docker-compose -f docker-compose.yml up -d

# Verify all services
docker-compose ps
```

### Using Private Registry

```bash
# Build with registry prefix
docker build -t registry.example.com/loan-ai-backend:1.0 ./backend

# Push to registry
docker push registry.example.com/loan-ai-backend:1.0

# Use in docker-compose.yml
services:
  backend:
    image: registry.example.com/loan-ai-backend:1.0
```

## Environment Variable Override

Override in command line:

```bash
docker-compose -e GROQ_API_KEY=xyz up -d
```

Or create separate .env files:

```bash
docker-compose --env-file .env.prod up -d
```

## Docker Compose Override

Create `docker-compose.override.yml` for local development:

```yaml
version: '3.8'
services:
  backend:
    ports:
      - "8001:8000"
  frontend:
    ports:
      - "3001:3000"
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Build Docker Images
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build images
        run: docker-compose build
      - name: Push to registry
        run: docker-compose push
```

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [MongoDB Docker Image](https://hub.docker.com/_/mongo)
- [Node.js Docker Image](https://hub.docker.com/_/node)
- [Python Docker Image](https://hub.docker.com/_/python)
