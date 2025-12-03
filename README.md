# Telegram Stats Bot

A Telegram channel statistics tracker with a modern web dashboard.

## Features

- 📊 **Real-time Analytics**: Track views, reactions, replies, and forwards
- 📈 **Interactive Charts**: Visualize engagement metrics over time
- 🔄 **Auto Scraping**: Background scraping of channel messages
- 🎨 **Modern UI**: Built with Nuxt 3 and Nuxt UI
- 🐳 **Docker Ready**: Easy deployment with Docker Compose

## Quick Start with Docker 🐳

The easiest way to run this project:

```bash
# 1. Clone the repository
git clone <repo-url>
cd Telegram-StatsBot

# 2. Setup environment
cp .env.example .env

# 3. Edit .env and add your Telegram API credentials
# Get them from https://my.telegram.org
# API_ID=your_api_id
# API_HASH=your_api_hash

# 4. Start all services
docker-compose up -d

# 5. Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
```

📖 **[Full Docker Documentation](README.Docker.md)**

## Manual Setup

### Prerequisites

- Python 3.11+
- Node.js 20+
- pnpm 9+
- PostgreSQL 15+

### Backend Setup

```bash
cd bot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup .env
cp .env.example .env
# Edit .env with your credentials

# Run migrations (database auto-created)
python main.py
```

### Frontend Setup

```bash
cd webapp

# Install dependencies
pnpm install

# Run development server
pnpm dev
```

Access:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Project Structure

```
Telegram-StatsBot/
├── bot/                    # Python FastAPI backend
│   ├── main.py            # Application entry point
│   ├── api.py             # API routes
│   ├── database.py        # Database connection
│   ├── models.py          # SQLModel models
│   ├── repository.py      # Data access layer
│   ├── service.py         # Business logic
│   ├── telegram_client.py # Pyrogram client
│   └── Dockerfile         # Backend Docker image
├── webapp/                # Nuxt 3 frontend
│   ├── app/
│   │   ├── pages/        # Route pages
│   │   ├── components/   # Vue components
│   │   ├── composables/  # Composition functions
│   │   └── utils/        # Utility functions
│   └── Dockerfile        # Frontend Docker image
├── docker-compose.yml    # Docker orchestration
└── README.md            # This file
```

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **Pyrogram**: Telegram MTProto API client
- **SQLModel**: SQL database with type hints
- **PostgreSQL**: Database

### Frontend
- **Nuxt 3**: Vue.js framework
- **Nuxt UI**: Component library
- **Vite**: Build tool
- **pnpm**: Package manager

## Key Features Explained

### Date Picker Fix
The project includes a critical fix for timezone-related date range issues. The `formatDateForAPI()` utility ensures dates are sent to the backend without timezone conversion, preventing ±1 day shifts.

### Scraping
Channels are scraped in the background using Pyrogram. Messages are stored with their engagement metrics and aggregated into daily statistics.

### Analytics
The dashboard displays:
- Total posts, views, reactions, replies, forwards
- Daily breakdown charts
- Engagement metrics over time

## Environment Variables

### Backend (.env in bot/)
```env
API_ID=your_telegram_api_id
API_HASH=your_telegram_api_hash
DATABASE_URL=postgresql://user:pass@localhost/dbname  # Optional, defaults to SQLite
```

### Frontend (.env in webapp/)
```env
NUXT_PUBLIC_API_BASE=http://localhost:8000  # Backend API URL
```

## Development

### Backend Development
```bash
cd bot
python main.py
# Server runs on http://localhost:8000
# Auto-reload not enabled by default
```

### Frontend Development
```bash
cd webapp
pnpm dev
# Hot reload enabled on http://localhost:3000
```

## Deployment

See [README.Docker.md](README.Docker.md) for Docker deployment guide.

For production:
1. Use environment-specific variables
2. Set up SSL/TLS with reverse proxy
3. Configure database backups
4. Monitor service health

## License

MIT License - see LICENSE file for details

## Contributing

Contributions welcome! Please open an issue or PR.
