<script setup lang="ts">
import type { Channel } from '~/types/telegram'

const props = defineProps<{
  channel: Channel | null
}>()

const open = defineModel<boolean>('open', { required: true })
const { t } = useI18n()

const formatDate = (dateString: string | undefined) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleString()
}
</script>

<template>
  <UModal v-model:open="open" :title="t('channelDetails')">
    <template #body>
      <div v-if="channel" class="space-y-4">
        <!-- Channel Header -->
        <div class="flex items-start gap-4 pb-4 border-b border-default">
          <UAvatar
            :src="channel.photo_file_id ? `https://ui-avatars.com/api/?name=${encodeURIComponent(channel.title)}` : undefined"
            :alt="channel.title"
            size="xl"
          />
          <div class="flex-1">
            <h3 class="text-xl font-semibold text-highlighted">{{ channel.title }}</h3>
            <p class="text-muted">@{{ channel.username || 'N/A' }}</p>
          </div>
        </div>

        <!-- Channel Info -->
        <div class="space-y-3">
          <h4 class="font-semibold text-highlighted">{{ t('channelInfo') }}</h4>
          
          <div class="grid grid-cols-2 gap-4">
            <div>
              <p class="text-xs text-muted uppercase mb-1">{{ t('subscribers') }}</p>
              <p class="font-semibold">{{ channel.subscriber_count?.toLocaleString() || 0 }}</p>
            </div>
            
            <div>
              <p class="text-xs text-muted uppercase mb-1">{{ t('type') }}</p>
              <p class="font-semibold">{{ channel.type || 'N/A' }}</p>
            </div>
            
            <div>
              <p class="text-xs text-muted uppercase mb-1">Channel ID</p>
              <p class="font-mono text-sm">{{ channel.channel_id }}</p>
            </div>
            
            <div>
              <p class="text-xs text-muted uppercase mb-1">{{ t('addedAt') }}</p>
              <p class="text-sm">{{ formatDate(channel.added_at) }}</p>
            </div>
          </div>

          <div v-if="channel.description">
            <p class="text-xs text-muted uppercase mb-1">{{ t('description') }}</p>
            <p class="text-sm">{{ channel.description }}</p>
          </div>
          <div v-else>
            <p class="text-xs text-muted uppercase mb-1">{{ t('description') }}</p>
            <p class="text-sm text-muted italic">{{ t('noDescription') }}</p>
          </div>
          
          <div v-if="channel.linked_chat_id">
            <p class="text-xs text-muted uppercase mb-1">{{ t('linkedChat') }}</p>
            <p class="font-mono text-sm">{{ channel.linked_chat_id }}</p>
          </div>
        </div>

        <!-- Actions -->
        <div class="flex justify-end gap-2 pt-4 border-t border-default">
          <UButton
            :label="t('openChannelLink')"
            icon="i-lucide-external-link"
            color="neutral"
            variant="outline"
            :disabled="!channel?.username"
            @click="() => {
              if (channel?.username) {
                navigateTo(`https://t.me/${channel.username}`, { external: true, open: { target: '_blank' } })
              }
            }"
          />
          <UButton
            :label="t('cancel')"
            color="neutral"
            variant="subtle"
            @click="open = false"
          />
        </div>
      </div>
    </template>
  </UModal>
</template>
