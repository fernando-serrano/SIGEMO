<script setup lang="ts">
import { onMounted } from 'vue'

import { useEstadosCarneRun } from '@/features/sucamec/composables/useEstadosCarneRun'

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

const {
  cancelEstadosFlow,
  estadosDownloadUrl,
  estadosJob,
  estadosStatusLabel,
  globalRunCompactLabel,
  globalRunAlertVisible,
  globalRunMessage,
  globalRunTone,
  initializeEstadosRunState,
  isCancellingRun,
  isGlobalRunAlertCollapsed,
  isRunningEstadosJob,
  isTerminalEstadosJob,
  toggleGlobalRunAlertCollapsed,
} = useEstadosCarneRun()

onMounted(() => {
  void initializeEstadosRunState()
})
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

    <aside
      v-if="globalRunAlertVisible && estadosJob"
      class="sigemo-global-run-alert alert"
      :class="[
        `alert--${globalRunTone}`,
        {
          'sigemo-global-run-alert--terminal': isTerminalEstadosJob,
          'sigemo-global-run-alert--collapsed': isGlobalRunAlertCollapsed,
        },
      ]"
      aria-live="polite"
      aria-label="Estado de ejecucion de Estados SUCAMEC"
    >
      <div class="alert__icon" aria-hidden="true">
        <svg viewBox="0 0 24 24" fill="none">
          <path d="M12 8V12L15 14M21 12C21 16.97 16.97 21 12 21C7.03 21 3 16.97 3 12C3 7.03 7.03 3 12 3C16.97 3 21 7.03 21 12Z" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
        </svg>
      </div>
      <button
        type="button"
        class="alert__close sigemo-global-run-toggle"
        :aria-label="isGlobalRunAlertCollapsed ? 'Expandir estado de ejecucion' : 'Minimizar estado de ejecucion'"
        @click="toggleGlobalRunAlertCollapsed"
      >
        <svg v-if="isGlobalRunAlertCollapsed" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <path d="M9 6L15 12L9 18" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
        </svg>
        <svg v-else viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <path d="M15 6L9 12L15 18" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
        </svg>
      </button>
      <div class="alert__content">
        <div class="alert__title">{{ globalRunCompactLabel }}</div>
        <div v-if="!isGlobalRunAlertCollapsed" class="alert__message">{{ globalRunMessage }}</div>
        <div v-if="!isGlobalRunAlertCollapsed" class="sigemo-global-run-actions">
          <button
            v-if="isRunningEstadosJob"
            type="button"
            class="btn btn--ghost btn--sm"
            :disabled="isCancellingRun"
            @click="cancelEstadosFlow"
          >
            {{ isCancellingRun ? 'Cancelando...' : 'Cancelar ejecucion' }}
          </button>
          <a v-if="estadosDownloadUrl" class="btn btn--ghost btn--sm" :href="estadosDownloadUrl">
            Descargar resultados
          </a>
        </div>
      </div>
      <span class="sigemo-global-run-progress" aria-hidden="true" />
    </aside>
  </div>
</template>
