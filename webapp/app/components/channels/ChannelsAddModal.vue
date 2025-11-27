<script setup lang="ts">
import * as z from 'zod'
import type { FormSubmitEvent } from '@nuxt/ui'

// Zod schema for TelegramChannel
const schema = z.object({
  name: z.string().min(2, 'Channel name is too short'),
  username: z.string().min(3, 'Username too short').regex(/^[a-zA-Z0-9_]+$/, 'Invalid Telegram username'),
  link: z.string().url('Invalid URL format'),
  avatarSrc: z.string().url('Invalid URL for avatar'),
  status: z.enum(['active', 'inactive', 'restricted', 'banned']).default('active')
})

const open = ref(false)

type Schema = z.output<typeof schema>

const state = reactive<Partial<Schema>>({
  name: undefined,
  username: undefined,
  link: undefined,
  avatarSrc: undefined,
  status: 'active'
})

const toast = useToast()

async function onSubmit(event: FormSubmitEvent<Schema>) {
  // Normally call API
  // await $fetch('/api/channels', { method: 'POST', body: event.data })

  toast.add({
    title: 'Success',
    description: `New channel "${event.data.name}" added`,
    color: 'success'
  })

  // Reset form
  Object.assign(state, {
    name: undefined,
    username: undefined,
    link: undefined,
    avatarSrc: undefined,
    status: 'active'
  })

  open.value = false
}
</script>

<template>
  <UButton label="New Channel" icon="i-lucide-plus" @click="open = true" />

  <UModal v-model:open="open" title="New Telegram Channel" description="Add a new channel to monitor">
    <template #body>
      <UForm :schema="schema" :state="state" class="space-y-4" @submit="onSubmit">
        <UFormField label="Channel Name" placeholder="e.g., JavaDev Hub" name="name">
          <UInput v-model="state.name" class="w-full" />
        </UFormField>

        <UFormField label="Username" placeholder="e.g., javadevhub (without @)" name="username">
          <UInput v-model="state.username" class="w-full">
            <template #leading>
              <span class="text-muted/60">@</span>
            </template>
          </UInput>
        </UFormField>

        <UFormField label="Channel Link" placeholder="e.g., https://t.me/javadevhub" name="link">
          <UInput v-model="state.link" class="w-full" />
        </UFormField>

        <UFormField label="Avatar URL" placeholder="https://i.pravatar.cc/128" name="avatarSrc">
          <UInput v-model="state.avatarSrc" class="w-full" />
        </UFormField>

        <UFormField label="Status" name="status">
          <USelect
            v-model="state.status"
            :items="['active','inactive','restricted','banned']"
            class="capitalize"
            placeholder="Select status"
          />
        </UFormField>

        <div class="flex justify-end gap-2 pt-2">
          <UButton label="Cancel" color="neutral" variant="subtle" @click="open = false" />
          <UButton label="Create" color="primary" variant="solid" type="submit" />
        </div>
      </UForm>
    </template>
  </UModal>
</template>
