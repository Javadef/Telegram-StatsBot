import type { Channel } from '~/types/telegram'

export default defineEventHandler(async () => {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase || 'http://localhost:8000'

  try {
    const channels = await $fetch<Channel[]>(`${apiBase}/api/channels`)
    return channels
  } catch (error) {
    console.error('Failed to fetch channels from API:', error)
    throw createError({
      statusCode: 500,
      statusMessage: 'Failed to fetch channels from Telegram API'
    })
  }
})
