<script setup lang="ts">
import { sub } from 'date-fns'
import type { Range } from '~/types'
import type { Channel } from '~/types/telegram'

const { t } = useI18n()

// Fetch channels
const { data: channels, refresh: refreshChannels } = await useFetch<Channel[]>('/api/channels', {
  lazy: true
})

// Selected channel
const selectedChannel = ref<Channel | null>(null)
const selectedChannelId = ref<number | undefined>(undefined)

// Set first channel as default
watchEffect(() => {
  if (channels.value && channels.value.length > 0 && !selectedChannel.value) {
    selectedChannel.value = channels.value[0] || null
    selectedChannelId.value = channels.value[0]?.id
  }
})

// Update selected channel when ID changes
watch(selectedChannelId, (newId) => {
  if (newId && channels.value) {
    selectedChannel.value = channels.value.find(c => c.id === newId) || null
  }
})

// Date range - default last 30 days
const range = ref<Range>({
  start: sub(new Date(), { days: 30 }),
  end: new Date()
})

// Channel items for dropdown
const channelItems = computed(() => {
  if (!channels.value || channels.value.length === 0) return []
  return channels.value.map(channel => ({
    label: channel.title,
    value: channel.id,
    icon: 'i-lucide-radio'
  }))
})

// Check if we have channels
const hasChannels = computed(() => channels.value && channels.value.length > 0)
</script>

<template>
  <UDashboardPanel id="home">
    <template #header>
      <UDashboardNavbar :title="t('dashboard')" :ui="{ right: 'gap-3' }">
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>

        <template #right>
          <NuxtLink to="/channels">
            <UButton icon="i-lucide-plus" size="md" class="rounded-full" :label="t('addChannel')" />
          </NuxtLink>
        </template>
      </UDashboardNavbar>

      <UDashboardToolbar>
        <template #left>
          <USelect
            v-if="hasChannels"
            v-model="selectedChannelId"
            :items="channelItems"
            :placeholder="t('selectChannel')"
            class="min-w-[200px]"
          >
            <template #leading>
              <UIcon name="i-lucide-radio" class="size-5" />
            </template>
          </USelect>
          
          <HomeDateRangePicker v-if="hasChannels" v-model="range" />
        </template>
      </UDashboardToolbar>
    </template>

    <template #body>
      <div v-if="hasChannels && selectedChannel" class="space-y-4 sm:space-y-6">
        <HomeStats :channel="selectedChannel" :range="range" />
        <HomeChart :channel="selectedChannel" :range="range" />
        <HomeEngagement :channel="selectedChannel" :range="range" />
      </div>
      <div v-else class="flex items-center justify-center h-64">
        <div class="text-center space-y-3">
          <UIcon name="i-lucide-inbox" class="size-12 text-muted mx-auto" />
          <p class="text-muted">{{ t('noChannelsFound') }}</p>
          <p class="text-sm text-dimmed">{{ t('addChannelToGetStarted') }}</p>
          <NuxtLink to="/channels">
            <UButton :label="t('addChannel')" icon="i-lucide-plus" />
          </NuxtLink>
        </div>
      </div>
    </template>
  </UDashboardPanel>
</template>
