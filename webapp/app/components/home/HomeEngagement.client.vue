<script setup lang="ts">
import { format, parseISO } from 'date-fns'
import { VisXYContainer, VisLine, VisAxis, VisArea, VisCrosshair, VisTooltip, VisGroupedBar } from '@unovis/vue'
import type { Range } from '~/types'
import type { Channel } from '~/types/telegram'

const cardRef = useTemplateRef<HTMLElement | null>('cardRef')

const props = defineProps<{
  channel: Channel
  range: Range
}>()

type DataRecord = {
  date: Date
  reactions: number
  replies: number
  forwards: number
}

const { width } = useElementSize(cardRef)
const { fetchAnalytics } = useTelegramAPI()
const { t } = useI18n()

const data = ref<DataRecord[]>([])

const loadEngagementData = async () => {
  const startDate = props.range.start.toISOString().split('T')[0]
  const endDate = props.range.end.toISOString().split('T')[0]
  
  if (!props.channel.channel_id) return
  
  const analytics = await fetchAnalytics(props.channel.channel_id, startDate, endDate)
  
  if (analytics && analytics.daily_breakdown) {
    data.value = analytics.daily_breakdown.map(day => ({
      date: parseISO(day.date),
      reactions: day.reactions,
      replies: day.replies,
      forwards: day.forwards
    }))
  } else {
    data.value = []
  }
}

watch(
  [() => props.channel.id, () => props.range.start.getTime(), () => props.range.end.getTime()],
  loadEngagementData,
  { immediate: true }
)

const x = (_: DataRecord, i: number) => i

const totalReactions = computed(() => data.value.reduce((acc: number, { reactions }) => acc + reactions, 0))
const totalReplies = computed(() => data.value.reduce((acc: number, { replies }) => acc + replies, 0))
const totalForwards = computed(() => data.value.reduce((acc: number, { forwards }) => acc + forwards, 0))

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

const template = (d: DataRecord) => `${formatDate(d.date)}: ${d.reactions} reactions, ${d.replies} replies, ${d.forwards} forwards`
</script>

<template>
  <UCard ref="cardRef" :ui="{ root: 'overflow-visible', body: '!px-0 !pt-0 !pb-3' }">
    <template #header>
      <div class="space-y-2">
        <p class="text-xs text-muted uppercase mb-1.5">
          {{ t('engagementMetrics') }}
        </p>
        <div class="flex flex-wrap gap-4 text-sm">
          <div class="flex items-center gap-2">
            <div class="w-3 h-3 rounded-full bg-blue-500" />
            <span class="text-muted">{{ t('reactions') }}:</span>
            <span class="font-semibold text-highlighted">{{ formatNumber(totalReactions) }}</span>
          </div>
          <div class="flex items-center gap-2">
            <div class="w-3 h-3 rounded-full bg-green-500" />
            <span class="text-muted">{{ t('replies') }}:</span>
            <span class="font-semibold text-highlighted">{{ formatNumber(totalReplies) }}</span>
          </div>
          <div class="flex items-center gap-2">
            <div class="w-3 h-3 rounded-full bg-purple-500" />
            <span class="text-muted">{{ t('forwards') }}:</span>
            <span class="font-semibold text-highlighted">{{ formatNumber(totalForwards) }}</span>
          </div>
        </div>
      </div>
    </template>

    <VisXYContainer
      :data="data"
      :padding="{ top: 40 }"
      class="h-80"
      :width="width"
    >
      <VisGroupedBar
        :x="x"
        :y="[(d: DataRecord) => d.reactions, (d: DataRecord) => d.replies, (d: DataRecord) => d.forwards]"
        :color="['rgb(59, 130, 246)', 'rgb(34, 197, 94)', 'rgb(168, 85, 247)']"
      />

      <VisAxis
        type="x"
        :x="x"
        :tick-format="xTicks"
      />

      <VisCrosshair
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
