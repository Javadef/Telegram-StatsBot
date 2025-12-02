<script setup lang="ts">
import { format, sub } from 'date-fns'

const isOpen = defineModel<boolean>()
const emit = defineEmits(['success'])
const toast = useToast()

const state = reactive({
  channel_identifier: '',
  start_date: sub(new Date(), { days: 7 }),
  end_date: new Date()
})

const isLoading = ref(false)

async function onSubmit() {
  isLoading.value = true
  try {
    await $fetch('http://localhost:8000/api/scrape_channel', {
      method: 'POST',
      body: {
        channel_identifier: state.channel_identifier,
        start_date: format(state.start_date, 'yyyy-MM-dd'),
        end_date: format(state.end_date, 'yyyy-MM-dd')
      }
    })
    
    toast.add({ title: 'Muvaffaqiyatli', description: 'Ma\'lumot yig\'ish boshlandi!', color: 'success' })
    emit('success')
    isOpen.value = false
    state.channel_identifier = '' // reset
  } catch (error) {
    toast.add({ title: 'Xatolik', description: 'Kanal topilmadi yoki server xatosi.', color: 'error' })
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <UModal v-model="isOpen">
    <UCard>
      <template #header>
        <div class="flex items-center justify-between">
          <h3 class="text-base font-semibold leading-6 text-gray-900 dark:text-white">
            Yangi Skraperni Ishga Tushirish
          </h3>
          <UButton color="neutral" variant="ghost" icon="i-heroicons-x-mark-20-solid" class="-my-1" @click="isOpen = false" />
        </div>
      </template>

      <form @submit.prevent="onSubmit" class="space-y-4">
        <UFormGroup label="Kanal Username yoki ID" required>
          <UInput v-model="state.channel_identifier" placeholder="@durov yoki -100..." icon="i-lucide-at-sign" />
        </UFormGroup>

        <div class="grid grid-cols-2 gap-4">
          <UFormGroup label="Boshlanish Sanasi">
            <UPopover :popper="{ placement: 'bottom-start' }">
              <UButton icon="i-heroicons-calendar-days-20-solid" :label="format(state.start_date, 'd MMM, yyyy')" color="neutral" variant="solid" block />
              <template #content="{ close }">
                <DatePicker v-model="state.start_date" @close="close" />
              </template>
            </UPopover>
          </UFormGroup>

          <UFormGroup label="Tugash Sanasi">
            <UPopover :popper="{ placement: 'bottom-start' }">
              <UButton icon="i-heroicons-calendar-days-20-solid" :label="format(state.end_date, 'd MMM, yyyy')" color="neutral" variant="solid" block />
              <template #content="{ close }">
                <DatePicker v-model="state.end_date" @close="close" />
              </template>
            </UPopover>
          </UFormGroup>
        </div>

        <div class="flex justify-end gap-2 mt-4">
          <UButton label="Bekor qilish" color="neutral" variant="ghost" @click="isOpen = false" />
          <UButton type="submit" label="Boshlash" color="primary" :loading="isLoading" />
        </div>
      </form>
    </UCard>
  </UModal>
</template>