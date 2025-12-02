import type { Channel } from '~/types/telegram'
import type { TelegramChannel, ChannelStatus } from '~/types'

export const useChannelTransform = () => {
  /**
   * Transform API Channel to UI TelegramChannel format
   */
  const toUIChannel = (apiChannel: Channel, analytics?: { totalPosts?: number, totalViews?: number }): TelegramChannel => {
    // Determine avatar URL - use photo_file_id if available, otherwise fallback
    const avatarSrc = apiChannel.photo_file_id
      ? `https://api.telegram.org/file/bot${apiChannel.photo_file_id}`
      : `https://ui-avatars.com/api/?name=${encodeURIComponent(apiChannel.title)}&background=random`

    // Construct Telegram link
    const link = apiChannel.username
      ? `https://t.me/${apiChannel.username}`
      : `https://t.me/c/${Math.abs(apiChannel.channel_id)}`

    // Default status to 'active' - you can implement logic to derive this
    const status: ChannelStatus = 'active'

    return {
      id: apiChannel.id,
      channel_id: apiChannel.channel_id,
      name: apiChannel.title,
      username: apiChannel.username || '',
      link,
      avatar: { src: avatarSrc },
      subscribers: apiChannel.subscriber_count || 0,
      totalPosts: analytics?.totalPosts,
      totalViews: analytics?.totalViews,
      status
    }
  }

  /**
   * Transform array of API Channels to UI TelegramChannels
   */
  const toUIChannels = (apiChannels: Channel[]): TelegramChannel[] => {
    return apiChannels.map(channel => toUIChannel(channel))
  }

  return {
    toUIChannel,
    toUIChannels
  }
}
