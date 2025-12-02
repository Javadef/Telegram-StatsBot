<script setup lang="ts">
import { format, parseISO } from 'date-fns'
import { VisXYContainer, VisLine, VisAxis, VisArea, VisCrosshair, VisTooltip } from '@unovis/vue'
import type { Range } from '~/types'
import type { Channel } from '~/types/telegram'

const cardRef = useTemplateRef<HTMLElement | null>('cardRef')

const props = defineProps<{
  channel: Channel
  range: Range
}>()

type DataRecord = {
  date: Date
  views: number
  posts: number
}

const { width } = useElementSize(cardRef)
const { fetchAnalytics } = useTelegramAPI()
const { t } = useI18n()

const data = ref<DataRecord[]>([])

const loadChartData = async () => {
  const { formatDateForAPI } = await import('~/utils')
  const startDate = formatDateForAPI(props.range.start)
  const endDate = formatDateForAPI(props.range.end)
  
  const analytics = await fetchAnalytics(props.channel.channel_id, startDate, endDate)
  
  if (analytics && analytics.daily_breakdown) {
    // Parse dates correctly - they come from backend in Tashkent timezone
    data.value = analytics.daily_breakdown.map(day => ({
      date: parseISO(day.date), // This is just the date (YYYY-MM-DD), no timezone issues
      views: day.views,
      posts: day.posts
    }))
  } else {
    data.value = []
  }
}

watch(
  [() => props.channel.id, () => props.range.start.getTime(), () => props.range.end.getTime()],
  loadChartData,
  { immediate: true }
)

const x = (_: DataRecord, i: number) => i
const y = (d: DataRecord) => d.views

const totalViews = computed(() => data.value.reduce((acc: number, { views }) => acc + views, 0))
const totalPosts = computed(() => data.value.reduce((acc: number, { posts }) => acc + posts, 0))

const formatNumber = (num: number) => new Intl.NumberFormat('en').format(num)

const formatDate = (date: Date): string => {
  return format(date, 'd MMM')
}

const xTicks = (i: number) => {
  if (i === 0 || i === data.value.length - 1 || !data.value[i]) {
    return ''
  }

  return formatDate(data.value[i].date)
}

const template = (d: DataRecord) => `${formatDate(d.date)}: ${formatNumber(d.views)} views, ${d.posts} posts`
</script>

<template>
  <UCard ref="cardRef" :ui="{ root: 'overflow-visible', body: '!px-0 !pt-0 !pb-3' }">
    <template #header>
      <div class="space-y-2">
        <div>
          <p class="text-xs text-muted uppercase mb-1.5">
            {{ t('totalViews') }}
          </p>
          <p class="text-3xl text-highlighted font-semibold">
            {{ formatNumber(totalViews) }}
          </p>
        </div>
        <div>
          <p class="text-xs text-dimmed">
            {{ formatNumber(totalPosts) }} {{ t('postsInPeriod') }}
          </p>
        </div>
      </div>
    </template>

    <VisXYContainer
      :data="data"
      :padding="{ top: 40 }"
      class="h-96"
      :width="width"
    >
      <VisLine
        :x="x"
        :y="y"
        color="var(--ui-primary)"
      />
      <VisArea
        :x="x"
        :y="y"
        color="var(--ui-primary)"
        :opacity="0.1"
      />

      <VisAxis
        type="x"
        :x="x"
        :tick-format="xTicks"
      />

      <VisCrosshair
        color="var(--ui-primary)"
        :template="template"
      />

      <VisTooltip />
    </VisXYContainer>
  </UCard>
</template>

<style scoped>
.unovis-xy-container {
  --vis-crosshair-line-stroke-color: var(--ui-primary);
  --vis-crosshair-circle-stroke-color: var(--ui-bg);

  --vis-axis-grid-color: var(--ui-border);
  --vis-axis-tick-color: var(--ui-border);
  --vis-axis-tick-label-color: var(--ui-text-dimmed);

  --vis-tooltip-background-color: var(--ui-bg);
  --vis-tooltip-border-color: var(--ui-border);
  --vis-tooltip-text-color: var(--ui-text-highlighted);
}
</style>
