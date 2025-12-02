<script setup lang="ts">
import type { Channel } from '~/types/telegram'
// ⚠️ IMPORTANT: Import TableColumn for better column array typing
import type { TableColumn } from '@nuxt/ui/dist/runtime/types' 

// --- Props ---
const props = defineProps<{
  channels: Channel[]
}>()

// --- Columns ---
// We explicitly define the columns and use TableColumn<Channel> for type safety.
const columns: TableColumn<Channel>[] = [
  { key: 'title', label: 'Kanal Nomi' },
  { key: 'username', label: 'Link (Username)' },
  // NOTE: Key must exactly match the property name in the Channel interface
  { key: 'subscriber_count', label: 'Obunachilar' },
  { key: 'actions', label: '' }
]
</script>

<template>
  <UCard :ui="{ body: { padding: 'p-0' } }"> 
    <template #header>
      <h2 class="font-semibold text-lg">Kuzatilayotgan Kanallar</h2>
    </template>

    <UTable :rows="channels" :columns="columns">
      
      <template #title-data="{ row }">
        <div class="flex items-center gap-2">
          <UAvatar :alt="(row as Channel).title?.charAt(0)" size="sm" />
          <span class="font-medium text-gray-900 dark:text-white">
            {{ (row as Channel).title }}
          </span>
        </div>
      </template>

      <template #username-data="{ row }">
        <UBadge color="neutral" variant="subtle">@{{ (row as Channel).username }}</UBadge>
      </template>

      <template #subscriber_count-data="{ row }">
        {{ new Intl.NumberFormat('uz-UZ').format((row as Channel).subscriber_count ?? 0) }}
      </template>

      <template #actions-data="{ row }">
        <UButton 
          icon="i-lucide-bar-chart-2"
          size="xs"
          color="primary"
          variant="soft"
          label="Analitika"
          :to="`/channels/${(row as Channel).channel_id}`"
        />
      </template>

    </UTable>
  </UCard>
</template>