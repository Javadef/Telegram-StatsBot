#!/bin/bash

# Telegram StatsBot - Automated Deployment Script
# This script automates the deployment process on a fresh server

set -e  # Exit on any error

echo "=========================================="
echo "Telegram StatsBot - Automated Deployment"
echo "=========================================="
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    echo "Please do not run this script as root"
    exit 1
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Step 1: Install Docker if not present
if ! command_exists docker; then
    echo "📦 Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo "✅ Docker installed successfully"
else
    echo "✅ Docker is already installed"
fi

# Step 2: Install Docker Compose if not present
if ! command_exists docker-compose && ! docker compose version >/dev/null 2>&1; then
    echo "📦 Installing Docker Compose..."
    sudo apt-get update
    sudo apt-get install -y docker-compose-plugin
    echo "✅ Docker Compose installed successfully"
else
    echo "✅ Docker Compose is already installed"
fi

# Step 3: Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found!"
    echo "Creating .env file from template..."
    
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ Created .env file from .env.example"
        echo ""
        echo "⚠️  IMPORTANT: You must edit .env file with your actual credentials!"
        echo "   1. Get API_ID and API_HASH from https://my.telegram.org"
        echo "   2. Set a secure DB_PASSWORD"
        echo ""
        read -p "Press Enter to edit .env file now, or Ctrl+C to exit and edit manually..."
        nano .env || vi .env || echo "Please edit .env manually"
    else
        echo "❌ .env.example not found. Please create .env file manually."
        exit 1
    fi
else
    echo "✅ .env file exists"
fi

# Step 4: Check for session files
echo ""
echo "Checking for Telegram session files..."
if [ ! -f bot/telegram_scraper_session.session ]; then
    echo "⚠️  Telegram session files not found in bot/ directory"
    echo ""
    echo "You need to copy your session files to bot/ directory:"
    echo "  - telegram_scraper_session.session"
    echo "  - telegram_scraper_session.session-journal (if exists)"
    echo ""
    read -p "Have you copied the session files? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Please copy session files first, then run this script again."
        exit 1
    fi
else
    echo "✅ Session files found"
fi

# Step 5: Create sessions directory for Docker volume
if [ ! -d bot/sessions ]; then
    echo "Creating sessions directory..."
    mkdir -p bot/sessions
    if [ -f bot/telegram_scraper_session.session ]; then
        cp bot/telegram_scraper_session.session* bot/sessions/ 2>/dev/null || true
        echo "✅ Copied session files to sessions directory"
    fi
fi

# Step 6: Pull latest changes (if in git repo)
if [ -d .git ]; then
    echo ""
    echo "📥 Pulling latest changes from git..."
    git pull || echo "⚠️  Could not pull latest changes (might not be a concern)"
fi

# Step 7: Build and start Docker containers
echo ""
echo "🐳 Building and starting Docker containers..."
echo "This may take a few minutes on first run..."
echo ""

docker compose down 2>/dev/null || true
docker compose up -d --build

# Step 8: Wait for services to be healthy
echo ""
echo "⏳ Waiting for services to start (30 seconds)..."
sleep 30

# Step 9: Check service status
echo ""
echo "📊 Checking service status..."
docker compose ps

# Step 10: Show logs
echo ""
echo "📋 Recent logs:"
echo "----------------------------------------"
docker compose logs --tail=50

# Step 11: Test endpoints
echo ""
echo "🧪 Testing endpoints..."
if command_exists curl; then
    echo -n "Backend API: "
    if curl -s -f http://localhost:8000/api/channels > /dev/null; then
        echo "✅ Responding"
    else
        echo "⚠️  Not responding yet (may need more time)"
    fi
    
    echo -n "Frontend: "
    if curl -s -f http://localhost:3000 > /dev/null; then
        echo "✅ Responding"
    else
        echo "⚠️  Not responding yet (may need more time)"
    fi
fi

# Step 12: Get server IP
SERVER_IP=$(hostname -I | awk '{print $1}')

# Final instructions
echo ""
echo "=========================================="
echo "✅ Deployment Complete!"
echo "=========================================="
echo ""
echo "Your application should be accessible at:"
echo "  Frontend: http://$SERVER_IP:3000"
echo "  Backend API: http://$SERVER_IP:8000"
echo "  API Docs: http://$SERVER_IP:8000/docs"
echo ""
echo "Useful commands:"
echo "  View logs:        docker compose logs -f"
echo "  Restart services: docker compose restart"
echo "  Stop services:    docker compose down"
echo "  Update app:       git pull && docker compose up -d --build"
echo ""
echo "For production setup with domain and SSL, see DEPLOY.md"
echo ""

# Ask if user wants to see logs
read -p "Would you like to follow the logs? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker compose logs -f
fi
