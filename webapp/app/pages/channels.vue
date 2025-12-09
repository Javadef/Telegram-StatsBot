<script setup lang="ts">
import type { Channel } from '~/types/telegram'

const { t } = useI18n()
const { fetchChannels, deleteChannel } = useTelegramAPI()
const toast = useToast()

// Fetch channels
const { data: channels, status, refresh } = await useFetch<Channel[]>('/api/channels', {
  lazy: true
})

// Search and filters
const searchQuery = ref('')
const statusFilter = ref<string>('all')

// Channel details modal
const selectedChannel = ref<Channel | null>(null)
const detailsModalOpen = ref(false)

const viewDetails = (channel: Channel) => {
  selectedChannel.value = channel
  detailsModalOpen.value = true
}

// Delete functionality
const deletingChannelId = ref<number | null>(null)
const deletePopoverOpen = ref<Record<number, boolean>>({})

const handleDelete = async (channel: Channel) => {
  deletingChannelId.value = channel.id!
  const success = await deleteChannel(channel.id!)
  deletingChannelId.value = null
  
  if (success) {
    deletePopoverOpen.value[channel.id!] = false
    toast.add({
      title: 'Kanal o\'chirildi',
      description: `${channel.title} muvaffaqiyatli o'chirildi`,
      color: 'success'
    })
    // Remove from list
    if (channels.value) {
      channels.value = channels.value.filter(c => c.id !== channel.id)
    }
  } else {
    toast.add({
      title: 'Xatolik',
      description: 'Kanalni o\'chirishda xatolik yuz berdi',
      color: 'error'
    })
  }
}

// Filtered channels
const filteredChannels = computed(() => {
  if (!channels.value) return []
  
  return channels.value.filter(channel => {
    const matchesSearch = channel.title.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
                         (channel.username || '').toLowerCase().includes(searchQuery.value.toLowerCase())
    
    const matchesStatus = statusFilter.value === 'all' || 
                         (channel.type?.toLowerCase() === statusFilter.value.toLowerCase())
    
    return matchesSearch && matchesStatus
  })
})

const getStatusColor = (type: string | undefined) => {
  const typeMap: Record<string, 'success' | 'warning' | 'error' | 'neutral'> = {
    'CHANNEL': 'success',
    'GROUP': 'warning',
    'PRIVATE': 'neutral'
  }
  return typeMap[type || ''] || 'neutral'
}
</script>

<template>
  <UDashboardPanel id="channels">
    <template #header>
      <UDashboardNavbar :title="t('telegramChannels')">
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>

        <template #right>
          <ChannelsAddModal @success="refresh" />
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <!-- Filters -->
      <div class="flex flex-wrap items-center justify-between gap-3 mb-4">
        <UInput
          v-model="searchQuery"
          class="max-w-sm"
          icon="i-lucide-search"
          :placeholder="t('filterByUsername')"
        />

        <div class="flex flex-wrap items-center gap-2">
          <USelect
            v-model="statusFilter"
            :items="[
              { label: t('all'), value: 'all' },
              { label: 'Channel', value: 'CHANNEL' },
              { label: 'Group', value: 'GROUP' },
              { label: 'Private', value: 'PRIVATE' }
            ]"
            :ui="{ trailingIcon: 'group-data-[state=open]:rotate-180 transition-transform duration-200' }"
            :placeholder="t('filterStatus')"
            class="min-w-28"
          />
        </div>
      </div>

      <!-- Channels Grid -->
      <div v-if="status === 'pending'" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <UCard v-for="i in 6" :key="i" class="animate-pulse">
          <div class="flex items-start gap-3">
            <USkeleton class="size-12 rounded-full" />
            <div class="flex-1 space-y-2">
              <USkeleton class="h-4 w-32" />
              <USkeleton class="h-3 w-24" />
            </div>
          </div>
        </UCard>
      </div>

      <div v-else-if="filteredChannels.length === 0" class="flex items-center justify-center h-64">
        <div class="text-center space-y-3">
          <UIcon name="i-lucide-inbox" class="size-12 text-muted mx-auto" />
          <p class="text-muted">{{ t('noChannelsFound') }}</p>
        </div>
      </div>

      <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <UCard
          v-for="channel in filteredChannels"
          :key="channel.id"
          class="hover:bg-elevated/50 transition-colors cursor-pointer"
          @click="viewDetails(channel)"
        >
          <div class="space-y-3">
            <!-- Channel Header -->
            <div class="flex items-start gap-3">
              <UAvatar
                :src="`https://ui-avatars.com/api/?name=${encodeURIComponent(channel.title)}&background=random`"
                :alt="channel.title"
                size="lg"
              />
              <div class="flex-1 min-w-0">
                <h3 class="font-semibold text-highlighted truncate">{{ channel.title }}</h3>
                <p class="text-sm text-muted truncate">@{{ channel.username || 'N/A' }}</p>
              </div>
              <UBadge :color="getStatusColor(channel.type)" variant="subtle" size="sm">
                {{ channel.type || 'N/A' }}
              </UBadge>
            </div>

            <!-- Channel Stats -->
            <div class="grid grid-cols-2 gap-3 pt-3 border-t border-default">
              <div>
                <p class="text-xs text-muted uppercase">{{ t('subscribers') }}</p>
                <p class="font-semibold">{{ channel.subscriber_count?.toLocaleString() || 0 }}</p>
              </div>
              <div>
                <p class="text-xs text-muted uppercase">ID</p>
                <p class="font-mono text-xs truncate">{{ channel.channel_id }}</p>
              </div>
            </div>

            <!-- Actions -->
            <div class="flex gap-2 pt-2">
              <UButton
                :label="t('viewDetails')"
                color="primary"
                variant="soft"
                size="xs"
                block
                icon="i-lucide-info"
                @click.stop="viewDetails(channel)"
              />
              <UButton
                v-if="channel.username"
                icon="i-lucide-external-link"
                color="neutral"
                variant="ghost"
                size="xs"
                squareateTo(`https://t.me/${channel.username}`, { external: true, open: { target: '_blank' } })"
              />
              <div @click.stop class="inline-flex">
                <UPopover v-model:open="deletePopoverOpen[channel.id!]" :popper="{ placement: 'top' }">
                  <div class="p-1.5 rounded-md hover:bg-red-50 dark:hover:bg-red-900/20 text-red-500 cursor-pointer transition-colors flex items-center justify-center">
                    <UIcon v-if="deletingChannelId === channel.id" name="i-lucide-loader-2" class="w-4 h-4 animate-spin" />
                    <UIcon v-else name="i-lucide-trash-2" class="w-4 h-4" />
                  </div>
                  <template #content>
                    <div class="p-3 space-y-3 w-64">
                      <p class="text-sm font-medium">O'chirish?</p>
                      <p class="text-xs text-gray-600 dark:text-gray-400">
                        {{ channel.title }} va barcha ma'lumotlarni o'chirmoqchimisiz?
                      </p>
                      <div class="flex gap-2">
                        <UButton
                          label="Bekor qilish"
                          color="neutral"
                          variant="ghost"
                          size="xs"
                          block
                          @click="deletePopoverOpen[channel.id!] = false"
                        />
                        <UButton
                          label="O'chirish"
                          color="error"
                          size="xs"
                          block
                          :loading="deletingChannelId === channel.id"
                          @click="handleDelete(channel)"
                        />
                      </div>
                    </div>
                  </template>
                </UPopover>
              </div>
            </div>
          </div>
        </UCard>
      </div>
    </template>
  </UDashboardPanel>

  <!-- Channel Details Modal -->
  <ChannelsChannelDetailsModal v-model:open="detailsModalOpen" :channel="selectedChannel" />
</template>
