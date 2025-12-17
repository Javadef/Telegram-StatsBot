import type { ScrapeStatusResponse } from '~/types/telegram'

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase || 'http://localhost:8000'
  const identifier = getRouterParam(event, 'identifier')

  if (!identifier) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Channel identifier is required'
    })
  }

  try {
    const status = await $fetch<ScrapeStatusResponse>(`${apiBase}/api/scrape_status/${identifier}`)
    return status
  } catch (error) {
    console.error(`Failed to fetch scrape status for ${identifier}:`, error)
    throw createError({
      statusCode: 500,
      statusMessage: `Failed to fetch scrape status for ${identifier}`
    })
  }
})
