<script setup lang="ts">
import { CalendarDate, getLocalTimeZone } from '@internationalized/date'
import * as z from 'zod'
import type { FormSubmitEvent } from '@nuxt/ui'
import type { ScrapeRequest } from '~/types/telegram'

const { t } = useI18n()

// Zod schema for adding/scraping a Telegram channel
const schema = z.object({
  channel_identifier: z.string().min(1, 'Channel identifier is required'),
  start_date: z.any(),
  end_date: z.any().optional()
})

const emit = defineEmits(['success'])
const open = ref(false)
const isLoading = ref(false)

type Schema = z.output<typeof schema>

const state = reactive<Partial<Schema>>({
  channel_identifier: undefined,
  start_date: undefined,
  end_date: undefined
})

const toast = useToast()

async function onSubmit(event: FormSubmitEvent<Schema>) {
  isLoading.value = true
  
  try {
    const formatDate = (date: CalendarDate | undefined) => {
      if (!date) return undefined
      return `${date.year}-${String(date.month).padStart(2, '0')}-${String(date.day).padStart(2, '0')}`
    }

    const request: ScrapeRequest = {
      channel_identifier: event.data.channel_identifier,
      start_date: formatDate(event.data.start_date)!,
      end_date: formatDate(event.data.end_date)
    }

    const { data, error } = await useFetch('/api/scrape', {
      method: 'POST',
      body: request
    })
    
    if (error.value) {
      toast.add({
        title: t('error'),
        description: error.value.message || t('failedToStartScraping'),
        color: 'error'
      })
      return
    }

    if (data.value) {
      toast.add({
        title: t('scrapingStarted'),
        description: `${t('scrapingChannel')} "${event.data.channel_identifier}"`,
        color: 'success',
        icon: 'i-lucide-download'
      })

      // Emit success to refresh parent
      emit('success')

      // Reset form
      Object.assign(state, {
        channel_identifier: undefined,
        start_date: undefined,
        end_date: undefined
      })

      open.value = false
    }
  } catch (err: any) {
    toast.add({
      title: t('error'),
      description: err.message || t('failedToStartScraping'),
      color: 'error'
    })
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <UButton :label="t('addChannel')" icon="i-lucide-plus" @click="open = true" />

  <UModal v-model:open="open" :title="t('addTelegramChannel')" :description="t('startScrapingChannel')">
    <template #body>
      <UForm :schema="schema" :state="state" class="space-y-4" @submit="onSubmit">
        <UFormField :label="t('channelIdentifier')" :placeholder="t('channelIdentifierPlaceholder')" name="channel_identifier">
          <UInput v-model="state.channel_identifier" class="w-full" />
        </UFormField>

        <UFormField :label="t('startDate')" name="start_date">
          <UPopover>
            <UButton
              icon="i-lucide-calendar"
              color="neutral"
              variant="outline"
              block
            >
              {{ state.start_date ? `${state.start_date.year}-${String(state.start_date.month).padStart(2, '0')}-${String(state.start_date.day).padStart(2, '0')}` : t('selectDate') }}
            </UButton>
            <template #content>
              <UCalendar v-model="state.start_date" />
            </template>
          </UPopover>
        </UFormField>

        <UFormField :label="t('endDateOptional')" name="end_date">
          <UPopover>
            <UButton
              icon="i-lucide-calendar"
              color="neutral"
              variant="outline"
              block
            >
              {{ state.end_date ? `${state.end_date.year}-${String(state.end_date.month).padStart(2, '0')}-${String(state.end_date.day).padStart(2, '0')}` : t('selectDate') }}
            </UButton>
            <template #content>
              <UCalendar v-model="state.end_date" />
            </template>
          </UPopover>
        </UFormField>

        <div class="flex justify-end gap-2 pt-2">
          <UButton :label="t('cancel')" color="neutral" variant="subtle" :disabled="isLoading" @click="open = false" />
          <UButton :label="t('startScraping')" color="primary" variant="solid" type="submit" :loading="isLoading" />
        </div>
      </UForm>
    </template>
  </UModal>
</template>
