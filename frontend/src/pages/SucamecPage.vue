<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import TrackingPageHeader from '@/features/dashboard/components/TrackingPageHeader.vue'
import AppSidebar from '@/features/navigation/components/AppSidebar.vue'
import { useEstadosCarneRun } from '@/features/sucamec/composables/useEstadosCarneRun'
import AppShell from '@/shared/layouts/AppShell.vue'

const route = useRoute()
const mobileBreakpoint = window.matchMedia('(max-width: 1080px)')
const isSidebarOpen = ref(false)
const activeSucamecSection = computed(() => String(route.meta.sucamecSection ?? 'panel'))
const isCardStatusSection = computed(() => activeSucamecSection.value === 'estados-carne')
const {
  canStartEstadosFlow,
  cancelEstadosFlow,
  estadosDownloadUrl,
  estadosFeedback,
  estadosFeedbackTone,
  estadosJob,
  estadosStatusLabel,
  handleInputFileChange: setInputFile,
  initializeEstadosRunState,
  inputPreview,
  inputValidation,
  isCancellingRun,
  isRunningEstadosJob,
  isStartingRun,
  isUploadingInput,
  selectedInputFile,
  startEstadosFlow,
  sucamecGroup,
  uploadInputFile,
} = useEstadosCarneRun()

function openSidebar(): void {
  isSidebarOpen.value = true
}

function closeSidebar(): void {
  isSidebarOpen.value = false
}

function handleViewportChange(event: MediaQueryListEvent): void {
  if (!event.matches) {
    closeSidebar()
  }
}

function handleInputFileChange(event: Event): void {
  const input = event.target as HTMLInputElement
  setInputFile(input.files?.[0] ?? null)
}

onMounted(() => {
  void initializeEstadosRunState()

  if (mobileBreakpoint.matches) {
    closeSidebar()
  }

  mobileBreakpoint.addEventListener('change', handleViewportChange)
})

onBeforeUnmount(() => {
  mobileBreakpoint.removeEventListener('change', handleViewportChange)
})
</script>

<template>
  <AppShell :sidebar-open="isSidebarOpen" @close-sidebar="closeSidebar">
    <template #sidebar>
      <AppSidebar @close="closeSidebar" />
    </template>

    <section class="tracking-page" aria-label="Modulo SUCAMEC">
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

      <TrackingPageHeader />

      <section v-if="isCardStatusSection" class="card card--acrylic tracking-card" aria-label="Estados SUCAMEC">
        <header class="card__header tracking-card-header--space-between">
          <div class="sucamec-title-block">
            <span class="sucamec-icon sucamec-icon--accent" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none">
                <path d="M8 7H16M8 11H16M8 15H12M6 3H15L20 8V19C20 20.1 19.1 21 18 21H6C4.9 21 4 20.1 4 19V5C4 3.9 4.9 3 6 3Z" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
                <path d="M15 3V8H20" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
              </svg>
            </span>
            <div>
            <p class="card__header-title tracking-card-title">CONSULTA AUTOMATIZADA</p>
            <p class="tracking-empty" style="text-align: left; margin: 0;">
              Submodulo preparado para consultar estados mediante el flujo automatizado del portal SUCAMEC.
            </p>
            </div>
          </div>

          <span class="chip chip--info">Robot</span>
        </header>

        <div class="card__body" style="display: grid; gap: var(--fa-space-3);">
          <section class="users-access-panel">
            <div class="users-access-header">
              <p class="users-access-title">Estados</p>
              <p class="users-access-copy">Carga el Excel de entrada, selecciona el grupo y ejecuta el flujo Python/Playwright.</p>
            </div>

            <div class="users-access-summary-grid">
              <article class="users-access-summary-card">
                <span class="sucamec-card-icon" aria-hidden="true">
                  <svg viewBox="0 0 24 24" fill="none">
                    <path d="M9 11L12 14L20 6M20 12V18C20 19.1 19.1 20 18 20H6C4.9 20 4 19.1 4 18V6C4 4.9 4.9 4 6 4H15" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
                  </svg>
                </span>
                <span class="users-access-summary-value">{{ inputValidation?.total_records ?? 0 }}</span>
                <span class="users-access-summary-label">Registros validos</span>
              </article>
              <article class="users-access-summary-card">
                <span class="sucamec-card-icon" aria-hidden="true">
                  <svg viewBox="0 0 24 24" fill="none">
                    <path d="M12 8V12L15 14M21 12C21 16.97 16.97 21 12 21C7.03 21 3 16.97 3 12C3 7.03 7.03 3 12 3C16.97 3 21 7.03 21 12Z" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
                  </svg>
                </span>
                <span class="users-access-summary-value">{{ estadosStatusLabel }}</span>
                <span class="users-access-summary-label">Estado</span>
              </article>
              <article class="users-access-summary-card">
                <span class="sucamec-card-icon" aria-hidden="true">
                  <svg viewBox="0 0 24 24" fill="none">
                    <path d="M8 7H16M6 11H18M9 15H15M7 3H17C18.1 3 19 3.9 19 5V19C19 20.1 18.1 21 17 21H7C5.9 21 5 20.1 5 19V5C5 3.9 5.9 3 7 3Z" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
                  </svg>
                </span>
                <span class="users-access-summary-value">{{ sucamecGroup }}</span>
                <span class="users-access-summary-label">Grupo</span>
              </article>
            </div>
          </section>

          <section class="users-access-panel">
            <div class="users-access-header">
              <p class="users-access-title">Entrada y ejecucion</p>
              <p class="users-access-copy">El archivo se guarda en ESTADOS-GADSO/data/entrada_data y cada ejecucion usa el Excel cargado para ese job.</p>
            </div>

            <div class="users-form-grid users-form-grid--datos">
              <label class="tracking-field">
                <span class="input-label">Excel de entrada</span>
                <input class="input input--sm" type="file" accept=".xlsx" :disabled="isUploadingInput || isRunningEstadosJob" @change="handleInputFileChange" />
              </label>

              <label class="tracking-field">
                <span class="input-label">Grupo</span>
                <select v-model="sucamecGroup" class="select select--sm" :disabled="isRunningEstadosJob">
                  <option value="JV">J&amp;V Resguardo</option>
                  <option value="SELVA">Selva</option>
                  <option value="TODOS">Todos</option>
                </select>
              </label>
            </div>

            <div class="users-form-actions">
              <button type="button" class="btn btn--ghost" :disabled="!selectedInputFile || isUploadingInput || isRunningEstadosJob" @click="uploadInputFile">
                {{ isUploadingInput ? 'Validando...' : 'Cargar y validar' }}
              </button>
              <button type="button" class="btn btn--primary" :disabled="!canStartEstadosFlow" @click="startEstadosFlow">
                {{ isStartingRun || isRunningEstadosJob ? 'Ejecutando...' : 'Ejecutar consulta' }}
              </button>
              <button type="button" class="btn btn--ghost" :disabled="!isRunningEstadosJob || isCancellingRun" @click="cancelEstadosFlow">
                {{ isCancellingRun ? 'Cancelando...' : 'Cancelar ejecucion' }}
              </button>
              <a v-if="estadosDownloadUrl" class="btn btn--ghost" :href="estadosDownloadUrl">
                Descargar resultado
              </a>
            </div>

            <div v-if="estadosFeedback" class="alert" :class="`alert--${estadosFeedbackTone}`" role="alert">
              <div class="alert__content">
                <div class="alert__title">Estados</div>
                <div class="alert__message">{{ estadosFeedback }}</div>
              </div>
            </div>

            <section v-if="inputValidation" class="sucamec-preview" aria-label="Previsualizacion del Excel validado">
              <div class="sucamec-preview__header">
                <div>
                  <p class="users-access-title">Previsualizacion</p>
                  <p class="users-access-copy">
                    Muestra de 5 filas. Columna detectada: {{ inputValidation.document_column }}.
                  </p>
                </div>
                <span class="chip chip--info">{{ inputValidation.total_records }} registros</span>
              </div>

              <div class="table-shell">
                <table class="data-table">
                  <thead>
                    <tr>
                      <th>Fila</th>
                      <th>NRO DOCUMENTO</th>
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

            <pre v-if="estadosJob?.log_tail" class="tracking-empty" style="text-align: left; white-space: pre-wrap; max-height: 220px; overflow: auto;">{{ estadosJob.log_tail }}</pre>
          </section>
        </div>
      </section>

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
