<script setup lang="ts">
import type { Range, Stat } from '~/types'
import type { Channel } from '~/types/telegram'

const props = defineProps<{
  channel: Channel
  range: Range
}>()

const { t } = useI18n()
const { fetchAnalytics } = useTelegramAPI()

const formatNumber = (value: number): string => {
  return value.toLocaleString('en-US')
}

const stats = ref<Stat[]>([])

const loadStats = async () => {
  const startDate = props.range.start.toISOString().split('T')[0]
  const endDate = props.range.end.toISOString().split('T')[0]
  
  const analytics = await fetchAnalytics(props.channel.channel_id, startDate, endDate)
  
  if (!analytics || analytics.total_posts === 0) {
    stats.value = [
      { title: t('subscribers'), icon: 'i-lucide-users', value: formatNumber(props.channel.subscriber_count || 0) },
      { title: t('totalPosts'), icon: 'i-lucide-file-text', value: '0' },
      { title: t('totalViews'), icon: 'i-lucide-eye', value: '0' },
      { title: t('avgViewsPerPost'), icon: 'i-lucide-trending-up', value: '0' }
    ]
    return
  }
  
  const avgViewsPerPost = analytics.total_posts > 0 
    ? Math.round(analytics.total_views / analytics.total_posts)
    : 0
  
  stats.value = [
    {
      title: t('subscribers'),
      icon: 'i-lucide-users',
      value: formatNumber(props.channel.subscriber_count || 0)
    },
    {
      title: t('totalPosts'),
      icon: 'i-lucide-file-text',
      value: formatNumber(analytics.total_posts)
    },
    {
      title: t('totalViews'),
      icon: 'i-lucide-eye',
      value: formatNumber(analytics.total_views)
    },
    {
      title: t('avgViewsPerPost'),
      icon: 'i-lucide-trending-up',
      value: formatNumber(avgViewsPerPost)
    }
  ]
}

// Watch for changes
watch([() => props.channel.id, () => props.range.start.getTime(), () => props.range.end.getTime()], loadStats, { immediate: true })
</script>

<template>
  <UPageGrid class="lg:grid-cols-4 gap-4 sm:gap-6 lg:gap-px">
    <UPageCard
      v-for="(stat, index) in stats"
      :key="index"
      :icon="stat.icon"
      :title="stat.title"
      to="/channels"
      variant="subtle"
      :ui="{
        container: 'gap-y-1.5',
        wrapper: 'items-start',
        leading: 'p-2.5 rounded-full bg-primary/10 ring ring-inset ring-primary/25 flex-col',
        title: 'font-normal text-muted text-xs uppercase'
      }"
      class="lg:rounded-none first:rounded-l-lg last:rounded-r-lg hover:z-1"
    >
      <div class="flex items-center gap-2">
        <span class="text-2xl font-semibold text-highlighted">
          {{ stat.value }}
        </span>
      </div>
    </UPageCard>
  </UPageGrid>
</template>
