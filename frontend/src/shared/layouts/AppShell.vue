<script setup lang="ts">
withDefaults(
  defineProps<{
    sidebarOpen?: boolean
  }>(),
  {
    sidebarOpen: false,
  },
)

const emit = defineEmits<{
  (event: 'close-sidebar'): void
}>()
</script>

<template>
  <div class="dashboard-shell">
    <div
      class="dashboard-sidebar-layer"
      :class="{ 'dashboard-sidebar-layer--open': sidebarOpen }"
    >
      <button
        type="button"
        class="dashboard-sidebar-backdrop"
        aria-label="Cerrar menu lateral"
        @click="emit('close-sidebar')"
      />
      <div class="dashboard-sidebar-panel">
        <slot name="sidebar" />
      </div>
    </div>
    <main class="dashboard-main" aria-live="polite">
      <slot />
    </main>
  </div>
</template>
