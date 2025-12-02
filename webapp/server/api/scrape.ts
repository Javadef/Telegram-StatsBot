import type { ScrapeRequest, ScrapeStatusResponse } from '~/types/telegram'

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase || 'http://localhost:8000'
  
  const method = getMethod(event)

  // POST: Start a scrape
  if (method === 'POST') {
    const body = await readBody<ScrapeRequest>(event)
    
    if (!body.channel_identifier || !body.start_date) {
      throw createError({
        statusCode: 400,
        statusMessage: 'Missing required parameters: channel_identifier, start_date'
      })
    }

    try {
      const result = await $fetch<ScrapeStatusResponse>(`${apiBase}/api/scrape_channel`, {
        method: 'POST',
        body
      })
      return result
    } catch (error) {
      console.error('Failed to start scrape:', error)
      throw createError({
        statusCode: 500,
        statusMessage: 'Failed to start scrape task'
      })
    }
  }

  // GET: Get all scrape statuses
  if (method === 'GET') {
    try {
      const statuses = await $fetch<ScrapeStatusResponse[]>(`${apiBase}/api/scrape_status`)
      return statuses
    } catch (error) {
      console.error('Failed to fetch scrape statuses:', error)
      throw createError({
        statusCode: 500,
        statusMessage: 'Failed to fetch scrape statuses'
      })
    }
  }

  throw createError({
    statusCode: 405,
    statusMessage: 'Method not allowed'
  })
})
