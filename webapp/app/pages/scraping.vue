<script setup lang="ts">
import type { ScrapeStatusResponse } from '~/types/telegram'

const { t } = useI18n()

// Fetch scraping statuses with auto-refresh
const { data: statuses, refresh } = await useFetch<ScrapeStatusResponse[]>('/api/scrape', {
  lazy: true
})

// Auto-refresh every 5 seconds
const intervalId = setInterval(() => {
  refresh()
}, 5000)

// Cleanup on unmount
onUnmounted(() => {
  clearInterval(intervalId)
})

// Status color mapping
const getStatusColor = (status: string) => {
  const map: Record<string, 'success' | 'warning' | 'error' | 'neutral' | 'info'> = {
    'completed': 'success',
    'running': 'info',
    'initializing': 'warning',
    'failed': 'error',
    'pending': 'neutral',
    'paused': 'warning'
  }
  return map[status.toLowerCase()] || 'neutral'
}

// Status icon mapping
const getStatusIcon = (status: string) => {
  const map: Record<string, string> = {
    'completed': 'i-lucide-check-circle',
    'running': 'i-lucide-loader-circle',
    'initializing': 'i-lucide-clock',
    'failed': 'i-lucide-x-circle',
    'pending': 'i-lucide-clock',
    'paused': 'i-lucide-pause-circle'
  }
  return map[status.toLowerCase()] || 'i-lucide-circle'
}

// Format progress percentage
const formatProgress = (current: number, total: number) => {
  if (!total) return '0%'
  return `${Math.round((current / total) * 100)}%`
}
</script>

<template>
  <UDashboardPanel id="scraping">
    <template #header>
      <UDashboardNavbar :title="t('scrapingStatus')">
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>

        <template #right>
          <UButton
            icon="i-lucide-refresh-cw"
            color="neutral"
            variant="ghost"
            size="sm"
            @click="() => refresh()"
          >
            {{ t('refresh') }}
          </UButton>
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <div v-if="!statuses || statuses.length === 0" class="flex items-center justify-center h-64">
        <div class="text-center space-y-3">
          <UIcon name="i-lucide-inbox" class="size-12 text-muted mx-auto" />
          <p class="text-muted">{{ t('noScrapingTasks') }}</p>
          <p class="text-sm text-dimmed">{{ t('startScrapingFromChannels') }}</p>
          <NuxtLink to="/channels">
            <UButton :label="t('addChannel')" icon="i-lucide-plus" />
          </NuxtLink>
        </div>
      </div>

      <div v-else class="space-y-4">
        <UCard
          v-for="status in statuses"
          :key="status.channel_identifier"
          class="hover:bg-elevated/50 transition-colors"
        >
          <div class="space-y-4">
            <!-- Header -->
            <div class="flex items-start justify-between gap-4">
              <div class="flex items-start gap-3 flex-1 min-w-0">
                <UIcon
                  :name="getStatusIcon(status.status)"
                  :class="[
                    'size-6 shrink-0 mt-0.5',
                    status.status.toLowerCase() === 'running' ? 'animate-spin' : ''
                  ]"
                />
                <div class="flex-1 min-w-0">
                  <h3 class="font-semibold text-highlighted truncate">
                    {{ status.channel_identifier }}
                  </h3>
                  <p class="text-sm text-muted">
                    {{ status.error || status.status }}
                  </p>
                </div>
              </div>
              <UBadge :color="getStatusColor(status.status)" variant="subtle">
                {{ status.status }}
              </UBadge>
            </div>

            <!-- Progress Info -->
            <div v-if="status.messages_processed > 0" class="space-y-2">
              <div class="flex justify-between text-sm">
                <span class="text-muted">{{ t('progress') }}</span>
                <span class="font-medium">
                  {{ status.messages_processed }} {{ t('messagesProcessed') }}
                </span>
              </div>
              <div v-if="status.current_message_date" class="text-sm text-muted">
                {{ t('currentDate') }}: {{ new Date(status.current_message_date).toLocaleDateString() }}
              </div>
            </div>

            <!-- Timestamps (if available from channel data) --> available from channel data) -->
          </div>
        </UCard>
      </div>
    </template>
  </UDashboardPanel>
</template>
