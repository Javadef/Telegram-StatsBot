import type { AvatarProps } from '@nuxt/ui'

export type ChannelStatus = 'active' | 'inactive' | 'banned' | 'restricted'
export type SaleStatus = 'paid' | 'failed' | 'refunded'


export interface TelegramChannel {
  id: number
  name: string
  username: string
  link: string
  avatar: {
    src: string
  }
  subscribers: number
  totalPosts: number
  totalViews: number
  status: ChannelStatus
}

export interface User {
  id: number
  name: string
  email: string
  avatar?: AvatarProps
  status: UserStatus
  location: string
}

export interface Mail {
  id: number
  unread?: boolean
  from: User
  subject: string
  body: string
  date: string
}

export interface Member {
  name: string
  username: string
  role: 'member' | 'owner'
  avatar: AvatarProps
}

export interface Stat {
  title: string
  icon: string
  value: number | string
  variation: number
  formatter?: (value: number) => string
}

export interface Sale {
  id: string
  date: string
  status: SaleStatus
  email: string
  amount: number
}

export interface Notification {
  id: number
  unread?: boolean
  sender: User
  body: string
  date: string
}

export type Period = 'daily' | 'weekly' | 'monthly'

export interface Range {
  start: Date
  end: Date
}
