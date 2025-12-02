<script setup lang="ts">
import type { ScrapeStatus } from '~/types'

const props = defineProps<{
  channel: string
  status: ScrapeStatus
}>()

const statusColorMap = {
  blue: 'info',
  green: 'success',
  red: 'error',
  gray: 'neutral'
} as const

const statusColor = computed(() => statusColorMap[props.status.color])

const statusLabelMap = {
  running: 'Yuklanmoqda...',
  completed: 'Yakunlandi',
  failed: 'Xatolik',
  pending: 'Kutilmoqda',
  initializing: 'Tayyorlanmoqda',
  paused: 'To‘xtatilgan'
} as const

const statusLabel = computed(() => {
  return statusLabelMap[props.status.status] ?? props.status.status
})
</script>

<template>
  <UCard>
    <div class="flex justify-between items-start mb-2">
      <div class="font-medium truncate max-w-[70%]">
        {{ channel }}
      </div>
      <UBadge :color="statusColor" variant="subtle" size="xs">
        {{ statusLabel }}
      </UBadge>
    </div>

    <div class="space-y-2">
      <div class="flex justify-between text-sm text-gray-500">
        <span>Xabarlar:</span>
        <span class="font-bold text-gray-900 dark:text-white">{{ status.messages_processed }}</span>
      </div>
      
      <UProgress 
        v-if="status.status === 'running'" 
        animation="carousel" 
        size="xs" 
        color="primary" 
      />
      
      <div v-if="status.error" class="text-xs text-red-500 mt-2 bg-red-50 p-2 rounded">
        {{ status.error }}
      </div>
    </div>
  </UCard>
</template>