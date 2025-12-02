import type { Message } from '~/types/telegram'

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase || 'http://localhost:8000'
  
  const channelId = getRouterParam(event, 'channelId')
  const query = getQuery(event)
  const limit = query.limit ? Number(query.limit) : 100
  const offset = query.offset ? Number(query.offset) : 0

  if (!channelId) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Missing required parameter: channelId'
    })
  }

  try {
    const messages = await $fetch<Message[]>(`${apiBase}/api/messages/${channelId}`, {
      params: { limit, offset }
    })
    return messages
  } catch (error) {
    console.error('Failed to fetch messages from API:', error)
    throw createError({
      statusCode: 500,
      statusMessage: 'Failed to fetch messages from Telegram API'
    })
  }
})
