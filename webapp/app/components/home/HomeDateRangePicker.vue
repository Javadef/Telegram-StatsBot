<script setup lang="ts">
import { DateFormatter, getLocalTimeZone, CalendarDate, today } from '@internationalized/date'
import type { Range } from '~/types'

const { t } = useI18n()

const df = new DateFormatter('en-US', {
  dateStyle: 'medium'
})

const selected = defineModel<Range>({ required: true })
const isOpen = ref(false)

// Temporary range for calendar selection
const tempRange = ref<Range>({
  start: selected.value.start,
  end: selected.value.end
})

const ranges = [
  { label: 'Last 7 days', days: 7 },
  { label: 'Last 14 days', days: 14 },
  { label: 'Last 30 days', days: 30 },
  { label: 'Last 3 months', months: 3 },
  { label: 'Last 6 months', months: 6 },
  { label: 'Last year', years: 1 }
]

const toCalendarDate = (date: Date) => {
  return new CalendarDate(
    date.getFullYear(),
    date.getMonth() + 1,
    date.getDate()
  )
}

const calendarRange = computed({
  get: () => ({
    start: tempRange.value.start ? toCalendarDate(tempRange.value.start) : undefined,
    end: tempRange.value.end ? toCalendarDate(tempRange.value.end) : undefined
  }),
  set: (newValue: { start: CalendarDate | null, end: CalendarDate | null }) => {
    tempRange.value = {
      start: newValue.start ? newValue.start.toDate(getLocalTimeZone()) : new Date(),
      end: newValue.end ? newValue.end.toDate(getLocalTimeZone()) : new Date()
    }
  }
})

const isRangeSelected = (range: { days?: number, months?: number, years?: number }) => {
  if (!selected.value.start || !selected.value.end) return false

  const end = new Date()
  const start = new Date()

  if (range.days) {
    start.setDate(start.getDate() - range.days)
  } else if (range.months) {
    start.setMonth(start.getMonth() - range.months)
  } else if (range.years) {
    start.setFullYear(start.getFullYear() - range.years)
  }

  start.setHours(0, 0, 0, 0)
  end.setHours(23, 59, 59, 999)

  // Compare dates by day
  const selectedStart = new Date(selected.value.start)
  const selectedEnd = new Date(selected.value.end)
  selectedStart.setHours(0, 0, 0, 0)
  selectedEnd.setHours(0, 0, 0, 0)
  
  return selectedStart.getTime() === start.getTime() && selectedEnd.getTime() === end.getTime()
}

const selectRange = (range: { days?: number, months?: number, years?: number }) => {
  // Use regular JavaScript Date instead of @internationalized/date
  const end = new Date()
  const start = new Date()

  if (range.days) {
    start.setDate(start.getDate() - range.days)
  } else if (range.months) {
    start.setMonth(start.getMonth() - range.months)
  } else if (range.years) {
    start.setFullYear(start.getFullYear() - range.years)
  }

  // Reset time to start of day for consistent comparisons
  start.setHours(0, 0, 0, 0)
  end.setHours(23, 59, 59, 999)

  // Create new Date objects to force reactivity
  selected.value = {
    start: new Date(start.getTime()),
    end: new Date(end.getTime())
  }
  
  // Update temp range as well
  tempRange.value = {
    start: new Date(start.getTime()),
    end: new Date(end.getTime())
  }
  
  // Close popover
  isOpen.value = false
}

const applyRange = () => {
  // Create new Date objects to force reactivity
  selected.value = {
    start: new Date(tempRange.value.start.getTime()),
    end: new Date(tempRange.value.end.getTime())
  }
  isOpen.value = false
}

const cancelRange = () => {
  tempRange.value = { ...selected.value }
  isOpen.value = false
}

// Sync temp range when popover opens
watch(isOpen, (newValue) => {
  if (newValue) {
    tempRange.value = { ...selected.value }
  }
})
</script>

<template>
  <UPopover v-model:open="isOpen" :content="{ align: 'start', sideOffset: 8 }" :modal="true">
    <UButton
      color="neutral"
      variant="ghost"
      icon="i-lucide-calendar"
      class="data-[state=open]:bg-elevated group"
      size="sm"
    >
      <span class="truncate text-sm">
        <template v-if="selected.start">
          <template v-if="selected.end">
            {{ df.format(selected.start) }} - {{ df.format(selected.end) }}
          </template>
          <template v-else>
            {{ df.format(selected.start) }}
          </template>
        </template>
        <template v-else>
          {{ t('pickDate') }}
        </template>
      </span>

      <template #trailing>
        <UIcon name="i-lucide-chevron-down" class="shrink-0 text-dimmed size-4 group-data-[state=open]:rotate-180 transition-transform duration-200" />
      </template>
    </UButton>

    <template #content>
      <div class="flex flex-col max-w-full">
        <div class="flex flex-col sm:flex-row items-stretch sm:divide-x divide-default">
          <div class="flex sm:flex-col overflow-x-auto sm:overflow-visible p-2 sm:p-0 gap-1 sm:gap-0">
            <UButton
              v-for="(range, index) in ranges"
              :key="index"
              :label="range.label"
              color="neutral"
              variant="ghost"
              size="sm"
              class="rounded-md sm:rounded-none px-3 py-1.5 whitespace-nowrap"
              :class="[isRangeSelected(range) ? 'bg-elevated' : 'hover:bg-elevated/50']"
              @click="selectRange(range)"
            />
          </div>

          <UCalendar
            v-model="calendarRange"
            class="p-2"
            :number-of-months="1"
            range
          />
        </div>
        
        <!-- Action Buttons -->
        <div class="flex justify-end gap-2 p-3 border-t border-default">
          <UButton
            :label="t('cancel')"
            color="neutral"
            variant="ghost"
            size="sm"
            @click="cancelRange"
          />
          <UButton
            :label="t('apply')"
            color="primary"
            variant="solid"
            size="sm"
            @click="applyRange"
          />
        </div>
      </div>
    </template>
  </UPopover>
</template>
