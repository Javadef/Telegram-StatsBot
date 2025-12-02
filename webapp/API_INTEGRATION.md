# Telegram Stats Bot - API Integration

This webapp is now integrated with your FastAPI backend for Telegram channel statistics.

## Setup

1. **Environment Configuration**
   
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

   Update the API base URL if needed (default is `http://localhost:8000`):
   ```env
   NUXT_PUBLIC_API_BASE=http://localhost:8000
   ```

2. **Install Dependencies**
   ```bash
   pnpm install
   ```

3. **Run the Development Server**
   ```bash
   pnpm dev
   ```

## API Integration

### TypeScript Types

All types in `app/types/telegram.ts` now match your Python API models:

- `Channel` - Matches the SQLModel Channel from `bot/models.py`
- `Message` - Matches the Message model
- `AnalyticsResponse` - Matches analytics response with daily breakdown
- `ScrapeRequest` - Request body for starting a scrape
- `ScrapeStatusResponse` - Status of scraping tasks

### Composables

#### `useTelegramAPI()`

Main composable for API calls:

```typescript
const { 
  fetchChannels,        // Get all channels
  fetchChannel,         // Get single channel by ID
  fetchAnalytics,       // Get analytics for date range
  fetchMessages,        // Get messages with pagination
  startScrape,          // Start a scraping task
  fetchScrapeStatuses,  // Get all scrape statuses
  fetchScrapeStatus     // Get status for specific channel
} = useTelegramAPI()
```

**Example Usage:**

```typescript
// Fetch all channels
const channels = await fetchChannels()

// Fetch analytics
const analytics = await fetchAnalytics(
  channelId, 
  '2024-01-01', 
  '2024-01-31'
)

// Start a scrape
const status = await startScrape({
  channel_identifier: 'my_channel',
  start_date: '2024-01-01',
  end_date: '2024-01-31'
})
```

#### `useChannelTransform()`

Transform API data to UI-friendly format:

```typescript
const { toUIChannel, toUIChannels } = useChannelTransform()

// Transform single channel
const uiChannel = toUIChannel(apiChannel, { 
  totalPosts: 100, 
  totalViews: 50000 
})

// Transform array of channels
const uiChannels = toUIChannels(apiChannels)
```

### Server API Endpoints

The Nuxt server proxies requests to your FastAPI backend:

- `GET /api/channels` - List all channels
- `GET /api/channels/:id` - Get single channel
- `GET /api/analytics?channel_id=&start_date=&end_date=` - Get analytics
- `GET /api/messages/:channelId?limit=100&offset=0` - Get messages
- `POST /api/scrape` - Start scrape task
- `GET /api/scrape` - Get all scrape statuses

### Backend API Endpoints (FastAPI)

Your FastAPI backend should be running on `http://localhost:8000` with these endpoints:

- `POST /api/scrape_channel` - Start scraping a channel
- `GET /api/scrape_status` - Get all scrape statuses
- `GET /api/scrape_status/{channel_identifier}` - Get status for specific channel
- `GET /api/channels` - List all channels
- `GET /api/channels/{channel_id}` - Get channel details
- `GET /api/analytics` - Get analytics data
- `GET /api/messages/{channel_id}` - Get channel messages

## Architecture

```
Frontend (Nuxt) → Server API (Nuxt Proxy) → FastAPI Backend → Database
                                                            ↓
                                                    Telegram Client
```

The Nuxt server acts as a proxy to avoid CORS issues and provide a consistent API interface.

## Usage in Components

```vue
<script setup lang="ts">
const { fetchChannels } = useTelegramAPI()
const { toUIChannels } = useChannelTransform()

const channels = ref([])

onMounted(async () => {
  const apiChannels = await fetchChannels()
  channels.value = toUIChannels(apiChannels)
})
</script>

<template>
  <div>
    <div v-for="channel in channels" :key="channel.id">
      {{ channel.name }} - {{ channel.subscribers }} subscribers
    </div>
  </div>
</template>
```

## Development

Make sure your FastAPI backend is running before starting the Nuxt dev server:

```bash
# Terminal 1 - Start FastAPI backend
cd bot
uvicorn main:app --reload

# Terminal 2 - Start Nuxt dev server
cd webapp
pnpm dev
```
