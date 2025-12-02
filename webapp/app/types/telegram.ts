// types/telegram.ts
// Matches Python Channel model from api.py
export interface Channel {
  id: number
  channel_id: number
  title: string
  username: string
  description?: string
  subscriber_count: number
  photo_file_id?: string
  type?: string
  linked_chat_id?: number
  added_at?: string
}

// Matches Python Message model
export interface Message {
  id: number
  channel_id: number
  message_id: number
  date: string
  views: number
  reactions: number
  replies: number
  forwards: number
}

// Matches Python AnalyticsResponse
export interface DailyBreakdown {
  date: string
  posts: number
  views: number
  reactions: number
  replies: number
  forwards: number
}

export interface AnalyticsResponse {
  channel_id: number
  period_start: string
  period_end: string
  total_posts: number
  total_views: number
  total_reactions: number
  total_replies: number
  total_forwards: number
  daily_breakdown: DailyBreakdown[]
}

// Matches Python ScrapeRequest
export interface ScrapeRequest {
  channel_identifier: string
  start_date: string
  end_date?: string
}

// Matches Python ScrapeStatusResponse
export type ScrapeStatus = 'pending' | 'initializing' | 'running' | 'completed' | 'failed' | 'paused'

export interface ScrapeStatusResponse {
  channel_identifier: string
  status: ScrapeStatus
  messages_processed: number
  current_message_date?: string | null
  error?: string | null
}
