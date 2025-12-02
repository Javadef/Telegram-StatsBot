import type { AnalyticsResponse } from '~/types/telegram'

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase || 'http://localhost:8000'
  
  const query = getQuery(event)
  const { channel_id, start_date, end_date } = query

  if (!channel_id || !start_date || !end_date) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Missing required parameters: channel_id, start_date, end_date'
    })
  }

  try {
    const analytics = await $fetch<AnalyticsResponse>(`${apiBase}/api/analytics`, {
      params: {
        channel_id,
        start_date,
        end_date
      }
    })
    return analytics
  } catch (error: any) {
    // Log the error but return empty analytics instead of throwing
    console.warn(`Analytics not available for channel ${channel_id}:`, error?.message || error)
    
    // Return empty analytics response
    return {
      channel_id: Number(channel_id),
      period_start: String(start_date),
      period_end: String(end_date),
      total_posts: 0,
      total_views: 0,
      total_reactions: 0,
      total_replies: 0,
      total_forwards: 0,
      daily_breakdown: []
    } as AnalyticsResponse
  }
})
