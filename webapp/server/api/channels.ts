import type { TelegramChannel } from '~/types'

const channels: TelegramChannel[] = [
  {
    id: 1,
    name: 'JavaDev Hub',
    username: 'javadevhub',
    link: 'https://t.me/javadevhub',
    avatar: { src: 'https://i.pravatar.cc/128?u=channel1' },
    subscribers: 14500,
    totalPosts: 1280,
    totalViews: 520000,
    status: 'active'
  },
  {
    id: 2,
    name: 'Python World',
    username: 'pythonworld',
    link: 'https://t.me/pythonworld',
    avatar: { src: 'https://i.pravatar.cc/128?u=channel2' },
    subscribers: 32200,
    totalPosts: 2780,
    totalViews: 1840000,
    status: 'active'
  },
  {
    id: 3,
    name: 'Web Dev News',
    username: 'webdevnews',
    link: 'https://t.me/webdevnews',
    avatar: { src: 'https://i.pravatar.cc/128?u=channel3' },
    subscribers: 8900,
    totalPosts: 560,
    totalViews: 410000,
    status: 'inactive'
  },
  {
    id: 4,
    name: 'CyberSec Daily',
    username: 'cybersecdaily',
    link: 'https://t.me/cybersecdaily',
    avatar: { src: 'https://i.pravatar.cc/128?u=channel4' },
    subscribers: 54000,
    totalPosts: 4100,
    totalViews: 6200000,
    status: 'restricted'
  },
  {
    id: 5,
    name: 'CyberSec Daily',
    username: 'cybersecdaily',
    link: 'https://t.me/cybersecdaily',
    avatar: { src: 'https://i.pravatar.cc/128?u=channel4' },
    subscribers: 54000,
    totalPosts: 4100,
    totalViews: 6200000,
    status: 'restricted'
  },
    {
    id: 6,
    name: 'CyberSec Daily',
    username: 'cybersecdaily',
    link: 'https://t.me/cybersecdaily',
    avatar: { src: 'https://i.pravatar.cc/128?u=channel4' },
    subscribers: 54000,
    totalPosts: 4100,
    totalViews: 6200000,
    status: 'restricted'
  },
    {
    id: 7,
    name: 'CyberSec Daily',
    username: 'cybersecdaily',
    link: 'https://t.me/cybersecdaily',
    avatar: { src: 'https://i.pravatar.cc/128?u=channel4' },
    subscribers: 54000,
    totalPosts: 4100,
    totalViews: 6200000,
    status: 'restricted'
  },
      {
    id: 8,
    name: 'CyberSec Daily',
    username: 'cybersecdaily',
    link: 'https://t.me/cybersecdaily',
    avatar: { src: 'https://i.pravatar.cc/128?u=channel4' },
    subscribers: 54000,
    totalPosts: 4100,
    totalViews: 6200000,
    status: 'active'
  },
    {
    id: 9,
    name: 'CyberSec Daily',
    username: 'cybersecdaily',
    link: 'https://t.me/cybersecdaily',
    avatar: { src: 'https://i.pravatar.cc/128?u=channel4' },
    subscribers: 54000,
    totalPosts: 4100,
    totalViews: 6200000,
    status: 'restricted'
  },
  {
    id: 10,
    name: 'AI & ML Updates',
    username: 'aimlupdates',
    link: 'https://t.me/aimlupdates',
    avatar: { src: 'https://i.pravatar.cc/128?u=channel5' },
    subscribers: 26100,
    totalPosts: 1900,
    totalViews: 2100000,
    status: 'banned'
  }
  
  
]

export default defineEventHandler(() => {
  return channels
})
