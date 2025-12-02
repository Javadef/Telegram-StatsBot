import type { Channel, Message, AnalyticsResponse, ScrapeRequest, ScrapeStatusResponse } from '~/types/telegram'

export const useTelegramAPI = () => {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase || 'http://localhost:8000'

  // Fetch all channels
  const fetchChannels = async (): Promise<Channel[]> => {
    const { data, error } = await useFetch<Channel[]>(`${apiBase}/api/channels`)
    if (error.value) {
      console.error('Failed to fetch channels:', error.value)
      throw error.value
    }
    return data.value || []
  }

  // Fetch single channel by ID
  const fetchChannel = async (channelId: number): Promise<Channel | null> => {
    const { data, error } = await useFetch<Channel>(`${apiBase}/api/channels/${channelId}`)
    if (error.value) {
      console.error(`Failed to fetch channel ${channelId}:`, error.value)
      return null
    }
    return data.value || null
  }

  // Fetch analytics for a channel
  const fetchAnalytics = async (
    channelId: number,
    startDate: string,
    endDate: string
  ): Promise<AnalyticsResponse | null> => {
    try {
      const data = await $fetch<AnalyticsResponse>('/api/analytics', {
        params: {
          channel_id: channelId,
          start_date: startDate,
          end_date: endDate
        }
      })
      return data || null
    } catch (err) {
      console.error('Error fetching analytics:', err)
      return null
    }
  }

  // Fetch messages for a channel
  const fetchMessages = async (
    channelId: number,
    limit: number = 100,
    offset: number = 0
  ): Promise<Message[]> => {
    const { data, error } = await useFetch<Message[]>(`${apiBase}/api/messages/${channelId}`, {
      params: { limit, offset }
    })
    if (error.value) {
      console.error('Failed to fetch messages:', error.value)
      return []
    }
    return data.value || []
  }

  // Start a scrape task
  const startScrape = async (request: ScrapeRequest): Promise<ScrapeStatusResponse | null> => {
    const { data, error } = await useFetch<ScrapeStatusResponse>(`${apiBase}/api/scrape_channel`, {
      method: 'POST',
      body: request
    })
    if (error.value) {
      console.error('Failed to start scrape:', error.value)
      return null
    }
    return data.value || null
  }

  // Get all scrape statuses
  const fetchScrapeStatuses = async (): Promise<ScrapeStatusResponse[]> => {
    const { data, error } = await useFetch<ScrapeStatusResponse[]>(`${apiBase}/api/scrape_status`)
    if (error.value) {
      console.error('Failed to fetch scrape statuses:', error.value)
      return []
    }
    return data.value || []
  }

  // Get scrape status for a specific channel
  const fetchScrapeStatus = async (channelIdentifier: string): Promise<ScrapeStatusResponse | null> => {
    const { data, error } = await useFetch<ScrapeStatusResponse>(
      `${apiBase}/api/scrape_status/${channelIdentifier}`
    )
    if (error.value) {
      console.error(`Failed to fetch scrape status for ${channelIdentifier}:`, error.value)
      return null
    }
    return data.value || null
  }

  return {
    fetchChannels,
    fetchChannel,
    fetchAnalytics,
    fetchMessages,
    startScrape,
    fetchScrapeStatuses,
    fetchScrapeStatus
  }
}
