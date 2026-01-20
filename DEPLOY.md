# Server Deployment Guide

This guide will help you deploy the Telegram StatsBot on a production server using Docker.

## Prerequisites on Server

- Ubuntu/Debian server (or any Linux distribution)
- Docker Engine 20.10+ installed
- Docker Compose 2.0+ installed
- Git installed
- Open ports: 80, 443 (for web access), 3000, 8000

## Step 1: Install Docker on Server

If Docker is not installed, run these commands on your server:

```bash
# Update package list
sudo apt update

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose-plugin

# Add your user to docker group (optional, to run without sudo)
sudo usermod -aG docker $USER
newgrp docker

# Verify installation
docker --version
docker compose version
```

## Step 2: Clone Repository on Server

```bash
# Clone your repository
git clone https://github.com/Javadef/Telegram-StatsBot.git
cd Telegram-StatsBot
```

## Step 3: Set Up Environment Variables

Create a `.env` file in the project root:

```bash
nano .env
```

Add the following content (replace with your actual values):

```env
# Telegram API Configuration
# Get these from https://my.telegram.org
API_ID=your_actual_api_id
API_HASH=your_actual_api_hash

# Database Configuration
DB_PASSWORD=your_secure_database_password_here

# Optional: Backend URL for frontend
# NUXT_PUBLIC_API_BASE=http://localhost:8000
```

**Important:** Make sure to replace:
- `your_actual_api_id` with your real Telegram API ID
- `your_actual_api_hash` with your real Telegram API Hash
- `your_secure_database_password_here` with a strong password

## Step 4: Copy Session Files to Server

You need to copy your local Telegram session files to the server. On your **local machine**:

### Option A: Using SCP (if you have SSH access)

```bash
# From your local machine, in the project directory
scp bot/telegram_scraper_session.session* username@your-server-ip:/path/to/Telegram-StatsBot/bot/
```

### Option B: Manual Transfer

1. Copy the following files from your local `bot/` folder:
   - `telegram_scraper_session.session`
   - `telegram_scraper_session.session-journal` (if exists)

2. Upload them to your server at: `Telegram-StatsBot/bot/`

### Option C: Create Sessions Directory for Docker

The docker-compose.yml uses a volume for sessions. You can:

1. Create a sessions directory inside the bot folder:
```bash
mkdir -p bot/sessions
```

2. Copy your session files there:
```bash
cp bot/telegram_scraper_session.session* bot/sessions/
```

## Step 5: Build and Start Services

On your server, run:

```bash
# Build and start all services in detached mode
docker compose up -d --build

# This will:
# 1. Build the backend (Python/FastAPI)
# 2. Build the frontend (Nuxt.js)
# 3. Start PostgreSQL database
# 4. Start all services
```

## Step 6: Verify Deployment

Check if all services are running:

```bash
# Check service status
docker compose ps

# View logs (all services)
docker compose logs -f

# View specific service logs
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f database
```

Expected output should show all services as "healthy" or "running".

## Step 7: Access Your Application

- **Frontend:** http://your-server-ip:3000
- **Backend API:** http://your-server-ip:8000
- **API Documentation:** http://your-server-ip:8000/docs

## Step 8: Set Up Production Domain (Optional but Recommended)

### Using Nginx as Reverse Proxy

1. Install Nginx:
```bash
sudo apt install nginx
```

2. Create Nginx configuration:
```bash
sudo nano /etc/nginx/sites-available/telegram-stats
```

3. Add this configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

4. Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/telegram-stats /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

5. Set up SSL with Let's Encrypt:
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## Maintenance Commands

### Update Application
```bash
cd Telegram-StatsBot
git pull
docker compose up -d --build
```

### Restart Services
```bash
docker compose restart
# Or restart specific service
docker compose restart backend
```

### Stop Services
```bash
docker compose down
```

### View Resource Usage
```bash
docker stats
```

### Backup Database
```bash
docker compose exec database pg_dump -U postgres telegram_stats > backup_$(date +%Y%m%d).sql
```

### Restore Database
```bash
cat backup_20260106.sql | docker compose exec -T database psql -U postgres -d telegram_stats
```

## Troubleshooting

### Services Won't Start
```bash
# Check logs for errors
docker compose logs

# Restart from scratch
docker compose down -v
docker compose up -d --build
```

### Backend Can't Connect to Database
- Wait 30 seconds for database health check
- Check `.env` file has correct `DB_PASSWORD`
- Verify: `docker compose ps database`

### Session Errors
- Ensure session files are properly copied to server
- Check file permissions: `chmod 644 bot/telegram_scraper_session.session*`
- You may need to regenerate session by running the bot locally first

### Port Already in Use
```bash
# Check what's using the port
sudo lsof -i :3000
sudo lsof -i :8000

# Stop the conflicting service or change ports in docker-compose.yml
```

## Security Recommendations

1. **Firewall Setup:**
```bash
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

2. **Change Default Passwords:** Make sure `.env` has strong passwords

3. **Regular Updates:**
```bash
# Update system
sudo apt update && sudo apt upgrade

# Update Docker images
docker compose pull
docker compose up -d
```

4. **Backup Strategy:** Set up automated backups of:
   - Database (daily)
   - Session files (weekly)
   - `.env` file (secure storage)

## Monitoring

### Check Service Health
```bash
# All services
docker compose ps

# Individual health
docker inspect telegram-stats-backend | grep -A 5 Health
docker inspect telegram-stats-frontend | grep -A 5 Health
```

### Resource Monitoring
```bash
# Real-time stats
docker stats

# Disk usage
docker system df
```

## Support

If you encounter issues:
1. Check logs: `docker compose logs -f`
2. Verify environment variables: `cat .env`
3. Check GitHub issues: https://github.com/Javadef/Telegram-StatsBot/issues
