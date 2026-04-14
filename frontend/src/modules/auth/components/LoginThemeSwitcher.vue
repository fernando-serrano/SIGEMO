<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

import type { ThemeName } from '../types'

const props = defineProps<{ modelValue: ThemeName }>()

const emit = defineEmits<{
  (event: 'update:modelValue', value: ThemeName): void
}>()

const rootRef = ref<HTMLElement | null>(null)
const isOpen = ref(false)

const options: Array<{ label: string; short: string; value: ThemeName; kind: 'light' | 'dark' | 'corp' | 'corp-dark' }> = [
  { label: 'Light', short: 'Light', value: 'dark', kind: 'light' },
  { label: 'Dark', short: 'Dark', value: 'corp-dark', kind: 'dark' },
  { label: 'Corp Mode', short: 'Corp', value: 'light', kind: 'corp' },
  { label: 'Corp Dark', short: 'Corp D.', value: 'corp', kind: 'corp-dark' },
]

const currentOption = computed(() => options.find((option) => option.value === props.modelValue))
const currentLabel = computed(() => currentOption.value?.short ?? 'Theme')

function toggleMenu(): void {
  isOpen.value = !isOpen.value
}

function selectTheme(value: ThemeName): void {
  emit('update:modelValue', value)
  isOpen.value = false
}

function handleDocumentClick(event: MouseEvent): void {
  const target = event.target as Node | null

  if (rootRef.value && target && !rootRef.value.contains(target)) {
    isOpen.value = false
  }
}

function handleEscKey(event: KeyboardEvent): void {
  if (event.key === 'Escape') {
    isOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleDocumentClick)
  document.addEventListener('keydown', handleEscKey)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleDocumentClick)
  document.removeEventListener('keydown', handleEscKey)
})
</script>

<template>
  <div id="theme-toggle" ref="rootRef" class="auth-theme-switch">
    <button
      type="button"
      class="badge badge--node auth-theme-trigger"
      :data-theme-kind="currentOption?.kind ?? 'light'"
      :aria-expanded="isOpen"
      aria-controls="theme-bubbles"
      aria-label="Cambiar estilo visual"
      @click="toggleMenu"
    >
      <svg
        v-if="currentOption?.kind === 'light'"
        width="16"
        height="16"
        viewBox="0 0 16 16"
        fill="none"
        stroke="currentColor"
        stroke-width="1.5"
        stroke-linecap="round"
        aria-hidden="true"
      >
        <circle cx="8" cy="8" r="3" />
        <line x1="8" y1="0.5" x2="8" y2="2.5" />
        <line x1="8" y1="13.5" x2="8" y2="15.5" />
        <line x1="0.5" y1="8" x2="2.5" y2="8" />
        <line x1="13.5" y1="8" x2="15.5" y2="8" />
        <line x1="2.7" y1="2.7" x2="4.1" y2="4.1" />
        <line x1="11.9" y1="11.9" x2="13.3" y2="13.3" />
        <line x1="2.7" y1="13.3" x2="4.1" y2="11.9" />
        <line x1="11.9" y1="4.1" x2="13.3" y2="2.7" />
      </svg>

      <svg
        v-else-if="currentOption?.kind === 'corp'"
        width="16"
        height="16"
        viewBox="0 0 16 16"
        fill="none"
        stroke="currentColor"
        stroke-width="1.5"
        stroke-linecap="round"
        stroke-linejoin="round"
        aria-hidden="true"
      >
        <rect x="1" y="5" width="14" height="10" rx="1" />
        <path d="M5 5V3.5A1.5 1.5 0 0 1 6.5 2h3A1.5 1.5 0 0 1 11 3.5V5" />
        <line x1="1" y1="10" x2="15" y2="10" />
      </svg>

      <svg
        v-else-if="currentOption?.kind === 'corp-dark'"
        width="16"
        height="16"
        viewBox="0 0 16 16"
        fill="none"
        stroke="currentColor"
        stroke-width="1.5"
        stroke-linecap="round"
        stroke-linejoin="round"
        aria-hidden="true"
      >
        <rect x="1" y="5" width="14" height="10" rx="1" />
        <path d="M5 5V3.5A1.5 1.5 0 0 1 6.5 2h3A1.5 1.5 0 0 1 11 3.5V5" />
        <line x1="1" y1="10" x2="15" y2="10" />
        <circle cx="8" cy="10" r="1.5" fill="currentColor" />
      </svg>

      <svg
        v-else
        width="16"
        height="16"
        viewBox="0 0 16 16"
        fill="none"
        stroke="currentColor"
        stroke-width="1.5"
        stroke-linecap="round"
        stroke-linejoin="round"
        aria-hidden="true"
      >
        <path d="M14 9.5A6.5 6.5 0 0 1 6.5 2 6.5 6.5 0 1 0 14 9.5z" />
      </svg>

      {{ currentLabel }}
    </button>

    <div id="theme-bubbles" class="auth-theme-bubbles" :class="{ 'auth-theme-bubbles--open': isOpen }" :aria-hidden="!isOpen">
      <button
        v-for="option in options"
        :key="option.value"
        type="button"
        class="badge badge--node auth-theme-bubble"
        :data-theme-kind="option.kind"
        :class="modelValue === option.value ? 'auth-theme-bubble--active' : 'auth-theme-bubble--idle'"
        @click="selectTheme(option.value)"
      >
        <svg
          v-if="option.kind === 'light'"
          width="16"
          height="16"
          viewBox="0 0 16 16"
          fill="none"
          stroke="currentColor"
          stroke-width="1.5"
          stroke-linecap="round"
          aria-hidden="true"
        >
          <circle cx="8" cy="8" r="3" />
          <line x1="8" y1="0.5" x2="8" y2="2.5" />
          <line x1="8" y1="13.5" x2="8" y2="15.5" />
          <line x1="0.5" y1="8" x2="2.5" y2="8" />
          <line x1="13.5" y1="8" x2="15.5" y2="8" />
          <line x1="2.7" y1="2.7" x2="4.1" y2="4.1" />
          <line x1="11.9" y1="11.9" x2="13.3" y2="13.3" />
          <line x1="2.7" y1="13.3" x2="4.1" y2="11.9" />
          <line x1="11.9" y1="4.1" x2="13.3" y2="2.7" />
        </svg>

        <svg
          v-else-if="option.kind === 'corp'"
          width="16"
          height="16"
          viewBox="0 0 16 16"
          fill="none"
          stroke="currentColor"
          stroke-width="1.5"
          stroke-linecap="round"
          stroke-linejoin="round"
          aria-hidden="true"
        >
          <rect x="1" y="5" width="14" height="10" rx="1" />
          <path d="M5 5V3.5A1.5 1.5 0 0 1 6.5 2h3A1.5 1.5 0 0 1 11 3.5V5" />
          <line x1="1" y1="10" x2="15" y2="10" />
        </svg>

        <svg
          v-else-if="option.kind === 'corp-dark'"
          width="16"
          height="16"
          viewBox="0 0 16 16"
          fill="none"
          stroke="currentColor"
          stroke-width="1.5"
          stroke-linecap="round"
          stroke-linejoin="round"
          aria-hidden="true"
        >
          <rect x="1" y="5" width="14" height="10" rx="1" />
          <path d="M5 5V3.5A1.5 1.5 0 0 1 6.5 2h3A1.5 1.5 0 0 1 11 3.5V5" />
          <line x1="1" y1="10" x2="15" y2="10" />
          <circle cx="8" cy="10" r="1.5" fill="currentColor" />
        </svg>

        <svg
          v-else
          width="16"
          height="16"
          viewBox="0 0 16 16"
          fill="none"
          stroke="currentColor"
          stroke-width="1.5"
          stroke-linecap="round"
          stroke-linejoin="round"
          aria-hidden="true"
        >
          <path d="M14 9.5A6.5 6.5 0 0 1 6.5 2 6.5 6.5 0 1 0 14 9.5z" />
        </svg>

        {{ option.label }}
      </button>
    </div>
  </div>
</template>
