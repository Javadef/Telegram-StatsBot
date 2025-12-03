# Docker Deployment Guide

This project is containerized with separate Docker images for the backend (Python/FastAPI) and frontend (Nuxt.js with pnpm).

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+

## Quick Start

1. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your Telegram API credentials:
   - Get `API_ID` and `API_HASH` from https://my.telegram.org
   - Set a secure `DB_PASSWORD`

2. **Build and start all services:**
   ```bash
   docker-compose up -d
   ```

3. **Check service status:**
   ```bash
   docker-compose ps
   ```

4. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Services

### Database (PostgreSQL)
- **Image:** `postgres:15-alpine`
- **Port:** 5432
- **Data:** Persisted in `postgres_data` volume

### Backend (Python/FastAPI)
- **Build:** `./bot/Dockerfile`
- **Port:** 8000
- **Dependencies:** PostgreSQL
- **Session:** Telegram session files are mounted as volumes

### Frontend (Nuxt.js/pnpm)
- **Build:** `./webapp/Dockerfile`
- **Port:** 3000
- **Dependencies:** Backend API

## Common Commands

### Start services
```bash
docker-compose up -d
```

### Stop services
```bash
docker-compose down
```

### Stop and remove volumes (⚠️ deletes database)
```bash
docker-compose down -v
```

### View logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f database
```

### Rebuild after code changes
```bash
# Rebuild all
docker-compose up -d --build

# Rebuild specific service
docker-compose up -d --build backend
docker-compose up -d --build frontend
```

### Execute commands in containers
```bash
# Backend shell
docker-compose exec backend /bin/bash

# Frontend shell
docker-compose exec frontend /bin/sh

# Database shell
docker-compose exec database psql -U postgres -d telegram_stats
```

### View resource usage
```bash
docker stats
```

## Development vs Production

### Development
The default `docker-compose.yml` is suitable for development with:
- Hot reloading disabled (rebuild required for changes)
- Ports exposed for direct access
- Logs visible via `docker-compose logs`

### Production
For production deployment:

1. **Use environment-specific compose file:**
   ```bash
   docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
   ```

2. **Set production environment variables:**
   ```bash
   # .env
   DB_PASSWORD=<strong-random-password>
   NUXT_PUBLIC_API_BASE=https://your-domain.com/api
   ```

3. **Use a reverse proxy (nginx/Traefik) for:**
   - SSL/TLS termination
   - Load balancing
   - Domain routing

4. **Backup database regularly:**
   ```bash
   docker-compose exec database pg_dump -U postgres telegram_stats > backup.sql
   ```

## Troubleshooting

### Backend won't start
- Check Telegram API credentials in `.env`
- Ensure database is healthy: `docker-compose ps database`
- View logs: `docker-compose logs backend`

### Frontend can't connect to backend
- Verify `NUXT_PUBLIC_API_BASE` environment variable
- Check backend is running: `curl http://localhost:8000/api/channels`
- Ensure both services are on same network

### Database connection errors
- Check `DATABASE_URL` matches `DB_PASSWORD` in `.env`
- Wait for database health check to pass
- Verify network connectivity: `docker-compose exec backend ping database`

### Reset everything
```bash
docker-compose down -v
docker-compose up -d --build
```

## Network Architecture

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│   Frontend  │────────▶│   Backend   │────────▶│  Database   │
│  (Nuxt.js)  │         │  (FastAPI)  │         │ (PostgreSQL)│
│   Port 3000 │         │   Port 8000 │         │   Port 5432 │
└─────────────┘         └─────────────┘         └─────────────┘
       │                       │                       │
       └───────────────────────┴───────────────────────┘
                  telegram-stats-network
```

## Volume Persistence

- **postgres_data**: Database files (survives container recreation)
- **Session files**: Telegram authentication (mounted from host)

## Health Checks

All services include health checks:
- **Database**: PostgreSQL ready check every 10s
- **Backend**: HTTP request to `/api/channels` every 30s
- **Frontend**: HTTP request to homepage every 30s

Use `docker-compose ps` to view health status.
