<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import TrackingPageHeader from '@/features/dashboard/components/TrackingPageHeader.vue'
import AppSidebar from '@/features/navigation/components/AppSidebar.vue'
import { useEstadosCarneRun } from '@/features/sucamec/composables/useEstadosCarneRun'
import { useResponsiveSidebar } from '@/shared/composables/useResponsiveSidebar'
import AppShell from '@/shared/layouts/AppShell.vue'

const route = useRoute()
const { isSidebarOpen, openSidebar, closeSidebar } = useResponsiveSidebar()
const isUploadConfirmModalOpen = ref(false)
const isPreviewModalOpen = ref(false)
const activeSucamecSection = computed(() => String(route.meta.sucamecSection ?? 'panel'))
const isCardStatusSection = computed(() => activeSucamecSection.value === 'estados-carne')

const {
  canStartEstadosFlow,
  estadosDownloadUrl,
  estadosFeedbackTone,
  estadosJob,
  estadosPanelMessage,
  estadosPanelTone,
  estadosStatusLabel,
  handleInputFileChange: setInputFile,
  initializeEstadosRunState,
  inputPreview,
  inputValidation,
  isRunningEstadosJob,
  isStartingRun,
  isUploadingInput,
  selectedInputFile,
  startEstadosFlow,
  sucamecGroup,
  uploadInputFile,
  uploadedFilename,
} = useEstadosCarneRun()

const executionSteps = [
  { id: 'archivo', label: 'Archivo', meta: 'Carga y valida el Excel.' },
  { id: 'grupo', label: 'Grupo', meta: 'Selecciona el grupo.' },
  { id: 'acciones', label: 'Ejecucion', meta: 'Ejecuta la consulta.' },
] as const

const selectedInputLabel = computed(() => selectedInputFile.value?.name || '')
const hasGroupSelection = computed(() => Boolean(sucamecGroup.value))
const hasInvalidInputFeedback = computed(() => Boolean(estadosPanelMessage.value && estadosFeedbackTone.value === 'danger' && !uploadedInputReady.value))
const selectedInputSizeLabel = computed(() => {
  const size = selectedInputFile.value?.size ?? 0
  if (!size) return ''
  if (size < 1024) return `${size} B`
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`
  return `${(size / (1024 * 1024)).toFixed(1)} MB`
})
const uploadedInputReady = computed(() => Boolean(uploadedFilename.value && inputValidation.value?.is_valid))
const groupLabel = computed(() => {
  if (!sucamecGroup.value) return '-- Seleccionar --'
  if (sucamecGroup.value === 'JV') return 'J&V Resguardo'
  if (sucamecGroup.value === 'SELVA') return 'Selva'
  return 'Todos'
})
const statusIndicatorTone = computed(() => {
  if (!estadosJob.value) return uploadedInputReady.value ? 'success' : 'info'
  if (estadosJob.value.status === 'success') return 'success'
  if (estadosJob.value.status === 'error') return 'danger'
  if (estadosJob.value.status === 'cancelled') return 'warning'
  return 'info'
})

const executionCurrentStepIndex = computed(() => {
  if (estadosJob.value?.status === 'running' || estadosJob.value?.status === 'success' || estadosJob.value?.status === 'cancelled' || estadosJob.value?.status === 'error') {
    return 2
  }
  if (uploadedInputReady.value && hasGroupSelection.value) {
    return 2
  }
  if (uploadedInputReady.value) {
    return 1
  }
  return 0
})

const executionFlowProgressPercent = computed(() => {
  const completedSteps = executionSteps.filter((_, index) => isExecutionStepDone(index)).length
  return `${Math.min(completedSteps, executionSteps.length - 1) / (executionSteps.length - 1)}`
})

function formatDateTime(value: string | null): string {
  if (!value) return 'Pendiente'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return 'Pendiente'
  return new Intl.DateTimeFormat('es-PE', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  }).format(date)
}

const flowTimeline = computed(() => {
  const job = estadosJob.value
  const isValidated = Boolean(inputValidation.value?.is_valid)
  const isStarted = Boolean(job?.created_at)
  const isExecuted = Boolean(job?.started_at || job?.finished_at)
  const isGenerated = Boolean(job?.has_result || job?.status === 'success')

  return [
    {
      label: 'Archivo validado',
      timestamp: isValidated ? formatDateTime(job?.created_at ?? null) : 'Pendiente',
      state: isValidated ? 'done' : 'pending',
    },
    {
      label: 'Job iniciado',
      timestamp: isStarted ? formatDateTime(job?.created_at ?? null) : 'Pendiente',
      state: isStarted ? 'done' : 'pending',
    },
    {
      label: 'Consulta ejecutada',
      timestamp: isExecuted ? formatDateTime(job?.started_at ?? job?.finished_at ?? null) : 'Pendiente',
      state: isExecuted ? (job?.status === 'running' ? 'current' : 'done') : 'pending',
    },
    {
      label: 'Resultado generado',
      timestamp: isGenerated ? formatDateTime(job?.finished_at ?? null) : 'Pendiente',
      state: isGenerated ? 'done' : job?.status === 'error' ? 'error' : 'pending',
    },
  ] as const
})

const flowCurrentStepIndex = computed(() => {
  const states = flowTimeline.value.map((node) => node.state)
  const activeIndex = states.findIndex((state) => state === 'current')
  if (activeIndex >= 0) return activeIndex
  const firstPending = states.findIndex((state) => state === 'pending' || state === 'error')
  if (firstPending <= 0) return 0
  return Math.max(0, firstPending - 1)
})

const flowProgressPercent = computed(() => {
  const completedNodes = flowTimeline.value.filter((node) => node.state === 'done').length
  return `${Math.min(completedNodes, flowTimeline.value.length - 1) / (flowTimeline.value.length - 1)}`
})

function isExecutionStepDone(index: number): boolean {
  if (index === 0) return uploadedInputReady.value
  if (index === 1) return uploadedInputReady.value && hasGroupSelection.value
  return Boolean(estadosJob.value?.status === 'success')
}

function isExecutionStepActive(index: number): boolean {
  return index === executionCurrentStepIndex.value
}

function handleInputFileChange(event: Event): void {
  const input = event.target as HTMLInputElement
  setInputFile(input.files?.[0] ?? null)
  if (input.files?.[0]) {
    isUploadConfirmModalOpen.value = true
  }
}

function closeUploadConfirmModal(): void {
  isUploadConfirmModalOpen.value = false
  if (!uploadedInputReady.value) {
    setInputFile(null)
  }
}

async function confirmUploadInput(): Promise<void> {
  if (!selectedInputFile.value) {
    isUploadConfirmModalOpen.value = false
    return
  }

  isUploadConfirmModalOpen.value = false
  await uploadInputFile()
}

function openPreviewModal(): void {
  if (!inputValidation.value) return
  isPreviewModalOpen.value = true
}

function closePreviewModal(): void {
  isPreviewModalOpen.value = false
}

onMounted(() => {
  void initializeEstadosRunState()
})
</script>

<template>
  <AppShell :sidebar-open="isSidebarOpen" @close-sidebar="closeSidebar">
    <template #sidebar>
      <AppSidebar @close="closeSidebar" />
    </template>

    <section class="users-page sucamec-page" aria-label="Modulo SUCAMEC">
      <div class="tracking-mobile-bar">
        <button
          type="button"
          class="btn btn--ghost tracking-mobile-menu"
          aria-label="Abrir menu lateral"
          @click="openSidebar"
        >
          <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path d="M4 7H20 M4 12H20 M4 17H20" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
          </svg>
          Menu
        </button>
      </div>

      <header class="users-hero">
        <div class="users-hero-copy">
          <TrackingPageHeader />
        </div>
      </header>

      <template v-if="isCardStatusSection">
        <section class="card card--acrylic tracking-card sucamec-panel">
          <header class="card__header">
            <p class="card__header-title tracking-card-title">Ejecucion</p>
            <div class="sucamec-inline-indicators" aria-label="Indicadores del flujo">
              <span class="badge badge--sm badge--outline" :class="`badge--${statusIndicatorTone}`">
                {{ inputValidation?.total_records ?? 0 }} registros
              </span>
              <span class="badge badge--sm badge--outline" :class="`badge--${statusIndicatorTone}`">
                {{ estadosStatusLabel }}
              </span>
              <span class="badge badge--sm badge--outline" :class="hasGroupSelection ? 'badge--info' : 'badge--secondary'">
                {{ groupLabel }}
              </span>
            </div>
          </header>

          <div class="card__body users-form-body">
            <div class="users-access-panel sucamec-panel-body">
              <div
                class="sucamec-mini-flow sucamec-mini-flow--3"
                :style="{ '--sucamec-flow-progress': executionFlowProgressPercent }"
                aria-label="Etapas de ejecucion"
              >
                <div
                  v-for="(step, index) in executionSteps"
                  :key="step.id"
                  class="sucamec-mini-flow__step"
                  :class="{
                    'sucamec-mini-flow__step--done': isExecutionStepDone(index),
                    'sucamec-mini-flow__step--active': isExecutionStepActive(index),
                  }"
                >
                  <div class="sucamec-mini-flow__node">
                    <span class="sucamec-mini-flow__bubble">
                      <svg
                        v-if="isExecutionStepDone(index)"
                        width="13"
                        height="13"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        stroke-width="3"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        aria-hidden="true"
                      >
                        <path d="M20 6L9 17L4 12" />
                      </svg>
                      <span v-else>{{ index + 1 }}</span>
                    </span>
                  </div>
                  <span class="sucamec-mini-flow__label">{{ step.label }}</span>
                  <span class="sucamec-mini-flow__meta">{{ step.meta }}</span>
                </div>
              </div>

              <div class="sucamec-step-panels">
                <section class="sucamec-block sucamec-file-block">
                  <div class="sucamec-file-row">
                    <label
                      class="tracking-field sucamec-file-card"
                      :class="{ 'sucamec-file-card--has-preview': uploadedInputReady }"
                    >
                      <input class="input input--sm sucamec-file-input" type="file" accept=".xlsx" :disabled="isUploadingInput || isRunningEstadosJob" @change="handleInputFileChange" />
                      <span class="sucamec-file-icon" aria-hidden="true">
                        <svg viewBox="0 0 24 24" fill="none">
                          <path d="M14 3H7C5.9 3 5 3.9 5 5V19C5 20.1 5.9 21 7 21H17C18.1 21 19 20.1 19 19V8L14 3Z" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
                          <path d="M14 3V8H19" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
                          <path d="M8.5 13.5H15.5M8.5 16.5H13.5" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" />
                        </svg>
                      </span>
                      <span class="sucamec-file-content">
                        <span class="sucamec-file-name" :title="selectedInputLabel || 'Selecciona un archivo Excel'">
                          {{ selectedInputLabel || 'Selecciona un archivo Excel' }}
                        </span>
                        <span class="sucamec-file-meta">
                          {{ selectedInputSizeLabel || '--' }}
                          <span aria-hidden="true">•</span>
                          {{ uploadedInputReady ? 'Archivo validado' : hasInvalidInputFeedback ? 'Archivo no valido' : selectedInputFile ? 'Archivo seleccionado' : 'Pendiente' }}
                        </span>
                      </span>
                    </label>

                    <button
                      v-if="uploadedInputReady"
                      type="button"
                      class="btn btn--outline btn--sm btn--icon sucamec-file-preview-btn"
                      title="Ver datos cargados"
                      aria-label="Ver datos cargados"
                      @click.stop="openPreviewModal"
                    >
                      <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
                        <path d="M2.5 12S6.5 5.5 12 5.5S21.5 12 21.5 12S17.5 18.5 12 18.5S2.5 12 2.5 12Z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round" />
                        <circle cx="12" cy="12" r="2.5" stroke="currentColor" stroke-width="1.8" />
                      </svg>
                    </button>

                  </div>
                </section>

                <section class="sucamec-block sucamec-group-block">
                  <label class="tracking-field sucamec-group-panel">
                    <select
                      v-model="sucamecGroup"
                      class="select select--sm"
                      :class="{ 'sucamec-select--placeholder': !hasGroupSelection }"
                      :disabled="isRunningEstadosJob"
                    >
                      <option value="">-- Seleccionar --</option>
                      <option value="JV">J&amp;V Resguardo</option>
                      <option value="SELVA">Selva</option>
                      <option value="TODOS">Todos</option>
                    </select>
                  </label>
                </section>

                <section class="sucamec-block sucamec-action-block">
                  <div class="sucamec-action-strip">
                    <button
                      type="button"
                      class="btn btn--primary btn--sm sucamec-command-btn sucamec-command-btn--compact"
                      :disabled="!canStartEstadosFlow"
                      title="Ejecutar consulta"
                      aria-label="Ejecutar consulta"
                      @click="startEstadosFlow"
                    >
                      <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
                        <path d="M8 6.5V17.5L17 12L8 6.5Z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round" />
                      </svg>
                      <span>{{ isStartingRun || isRunningEstadosJob ? 'EJECUTANDO' : 'EJECUTAR' }}</span>
                    </button>
                  </div>
                  <a
                    v-if="estadosDownloadUrl"
                    class="btn btn--outline btn--sm sucamec-download-link"
                    :href="estadosDownloadUrl"
                  >
                    <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
                      <path d="M12 4V15M12 15L7.5 10.5M12 15L16.5 10.5M5 19H19" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
                    </svg>
                    Descargar resultados
                  </a>
                </section>
              </div>

              <p
                v-if="estadosPanelMessage"
                class="sucamec-feedback"
                :class="`sucamec-feedback--${estadosPanelTone}`"
              >
                {{ estadosPanelMessage }}
              </p>
            </div>
          </div>
        </section>

        <section class="card card--acrylic tracking-card sucamec-panel">
          <header class="card__header">
            <p class="card__header-title tracking-card-title">Seguimiento</p>
            <p class="users-card-copy">Estado y progreso del flujo de ejecucion.</p>
          </header>

          <div class="card__body users-form-body">
            <div
              class="sucamec-mini-flow"
              :style="{ '--sucamec-flow-progress': flowProgressPercent }"
              aria-label="Progreso del flujo"
            >
              <div
                v-for="(node, index) in flowTimeline"
                :key="node.label"
                class="sucamec-mini-flow__step"
                :class="{
                  'sucamec-mini-flow__step--done': node.state === 'done',
                  'sucamec-mini-flow__step--active': node.state === 'current' || (node.state === 'pending' && index === flowCurrentStepIndex),
                  'sucamec-mini-flow__step--error': node.state === 'error',
                }"
              >
                <div class="sucamec-mini-flow__node">
                  <span class="sucamec-mini-flow__bubble">
                    <svg
                      v-if="node.state === 'done'"
                      width="13"
                      height="13"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="3"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      aria-hidden="true"
                    >
                      <path d="M20 6L9 17L4 12" />
                    </svg>
                    <span v-else>{{ index + 1 }}</span>
                  </span>
                </div>
                <span class="sucamec-mini-flow__label">{{ node.label }}</span>
                <span class="sucamec-mini-flow__meta">{{ node.timestamp }}</span>
              </div>
            </div>

            <details v-if="estadosJob?.log_tail" class="sucamec-log-disclosure">
              <summary class="sucamec-log-summary">
                <span>Ver log tecnico</span>
                <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
                  <path d="M6 9L12 15L18 9" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
                </svg>
              </summary>
              <pre class="tracking-empty sucamec-log">{{ estadosJob.log_tail }}</pre>
            </details>
          </div>
        </section>

        <div v-if="isUploadConfirmModalOpen" class="modal-overlay modal-overlay--open">
          <section class="modal modal--danger" role="dialog" aria-modal="true" aria-labelledby="sucamec-upload-title">
            <header class="modal__header">
              <p id="sucamec-upload-title" class="modal__title">Confirmar carga de Excel</p>
              <button type="button" class="modal__close" aria-label="Cerrar" @click="closeUploadConfirmModal">
                <span aria-hidden="true">&times;</span>
              </button>
            </header>

            <div class="modal__body">
              <p>
                Se cargara y validara <strong>{{ selectedInputLabel }}</strong>.
              </p>
            </div>

            <footer class="modal__footer">
              <button type="button" class="btn btn--outline btn--sm" @click="closeUploadConfirmModal">Cancelar</button>
              <button type="button" class="btn btn--danger btn--sm" :disabled="isUploadingInput" @click="confirmUploadInput">
                Confirmar carga
              </button>
            </footer>
          </section>
        </div>

        <div v-if="isPreviewModalOpen && inputValidation" class="modal-overlay modal-overlay--open">
          <section class="modal" role="dialog" aria-modal="true" aria-labelledby="sucamec-preview-title">
            <header class="modal__header">
              <p id="sucamec-preview-title" class="modal__title">Datos cargados</p>
              <button type="button" class="modal__close" aria-label="Cerrar" @click="closePreviewModal">
                <span aria-hidden="true">&times;</span>
              </button>
            </header>

            <div class="modal__body">
              <section class="sucamec-preview" aria-label="Previsualizacion del Excel validado">
                <div class="sucamec-preview__header">
                  <div class="sucamec-preview__title-group">
                    <p class="users-access-title sucamec-preview__title">
                      <span class="sucamec-preview__status-dot" aria-hidden="true"></span>
                      Excel validado
                    </p>
                    <p class="users-access-copy">
                      Muestra de 5 filas. Columna detectada: {{ inputValidation.document_column }}.
                    </p>
                  </div>
                  <span class="sucamec-preview__record-badge">{{ inputValidation.total_records }} registros</span>
                </div>

                <div class="table-shell">
                  <table class="data-table">
                    <thead>
                      <tr>
                        <th>Fila</th>
                        <th>Nro. documento</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="row in inputPreview" :key="`${row.row_number}-${row.nro_documento}`">
                        <td>{{ row.row_number }}</td>
                        <td>{{ row.nro_documento }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>

                <p v-if="inputValidation.omitted_rows_count" class="tracking-empty" style="text-align: left; margin: 0;">
                  {{ inputValidation.omitted_rows_count }} filas fueron omitidas por no tener NRO DOCUMENTO.
                </p>
              </section>
            </div>
          </section>
        </div>
      </template>

      <section v-else class="card card--acrylic tracking-card" aria-label="Resumen del modulo SUCAMEC">
        <div class="card__body" style="display: grid; gap: var(--fa-space-3);">
          <span class="chip chip--info">Modulo habilitado</span>
          <p class="tracking-empty" style="text-align: left;">
            SUCAMEC ya aparece por encima de SIGEMO en la navegacion principal y cuenta con una vista inicial lista
            para extenderse con procesos, reportes o formularios propios del modulo.
          </p>
        </div>
      </section>
    </section>
  </AppShell>
</template>
