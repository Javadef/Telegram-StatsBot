import type { Channel } from '~/types/telegram'

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase || 'http://localhost:8000'
  const id = getRouterParam(event, 'id')
  const method = getMethod(event)

  if (!id) {
    throw createError({
      statusCode: 400,
      statusMessage: 'Channel ID is required'
    })
  }

  // GET: Fetch a single channel
  if (method === 'GET') {
    try {
      const channel = await $fetch<Channel>(`${apiBase}/api/channels/${id}`)
      return channel
    } catch (error) {
      console.error(`Failed to fetch channel ${id}:`, error)
      throw createError({
        statusCode: 500,
        statusMessage: `Failed to fetch channel ${id}`
      })
    }
  }

  // DELETE: Delete a channel
  if (method === 'DELETE') {
    try {
      await $fetch(`${apiBase}/api/channels/${id}`, {
        method: 'DELETE'
      })
      return { success: true }
    } catch (error) {
      console.error(`Failed to delete channel ${id}:`, error)
      throw createError({
        statusCode: 500,
        statusMessage: `Failed to delete channel ${id}`
      })
    }
  }

  throw createError({
    statusCode: 405,
    statusMessage: 'Method not allowed'
  })
})
