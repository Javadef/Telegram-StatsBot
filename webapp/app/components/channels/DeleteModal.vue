<script setup lang="ts">
withDefaults(defineProps<{
  count?: number
}>(), {
  count: 0
})

const open = ref(false)
const toast = useToast()

async function onSubmit() {
  // TODO: Implement actual delete functionality via API
  await new Promise(resolve => setTimeout(resolve, 1000))
  
  toast.add({
    title: 'Channels Deleted',
    description: `${count} channel(s) deleted successfully`,
    color: 'success'
  })
  
  open.value = false
}
</script>

<template>
  <UModal
    v-model:open="open"
    :title="`Delete ${count} channel${count > 1 ? 's' : ''}`"
    :description="`Are you sure? This action cannot be undone.`"
  >
    <slot />

    <template #body>
      <div class="flex justify-end gap-2">
        <UButton
          label="Cancel"
          color="neutral"
          variant="subtle"
          @click="open = false"
        />
        <UButton
          label="Delete"
          color="error"
          variant="solid"
          loading-auto
          @click="onSubmit"
        />
      </div>
    </template>
  </UModal>
</template>
