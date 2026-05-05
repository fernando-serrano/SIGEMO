<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import TrackingPageHeader from '@/features/dashboard/components/TrackingPageHeader.vue'
import AppSidebar from '@/features/navigation/components/AppSidebar.vue'
import AppShell from '@/shared/layouts/AppShell.vue'

const route = useRoute()
const mobileBreakpoint = window.matchMedia('(max-width: 1080px)')
const isSidebarOpen = ref(false)
const activeSucamecSection = computed(() => String(route.meta.sucamecSection ?? 'panel'))
const isCardStatusSection = computed(() => activeSucamecSection.value === 'estados-carne')

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

onMounted(() => {
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

      <section v-if="isCardStatusSection" class="card card--acrylic tracking-card" aria-label="Estados de carné SUCAMEC">
        <header class="card__header tracking-card-header--space-between">
          <div>
            <p class="card__header-title tracking-card-title">CONSULTA AUTOMATIZADA</p>
            <p class="tracking-empty" style="text-align: left; margin: 0;">
              Submodulo preparado para consultar estados de carné mediante el flujo automatizado del portal SUCAMEC.
            </p>
          </div>

          <span class="chip chip--info">Robot</span>
        </header>

        <div class="card__body" style="display: grid; gap: var(--fa-space-3);">
          <section class="users-access-panel">
            <div class="users-access-header">
              <p class="users-access-title">Estados carné</p>
              <p class="users-access-copy">Aqui se conectara el boton de consulta con el servicio Python/Playwright del backend.</p>
            </div>

            <div class="users-access-summary-grid">
              <article class="users-access-summary-card">
                <span class="users-access-summary-value">0</span>
                <span class="users-access-summary-label">Consultas</span>
              </article>
              <article class="users-access-summary-card">
                <span class="users-access-summary-value">-</span>
                <span class="users-access-summary-label">Ultimo estado</span>
              </article>
              <article class="users-access-summary-card">
                <span class="users-access-summary-value">Headless</span>
                <span class="users-access-summary-label">Modo</span>
              </article>
            </div>
          </section>

          <section class="users-access-panel">
            <div class="users-access-header">
              <p class="users-access-title">Busqueda</p>
              <p class="users-access-copy">Espacio reservado para ingresar DNI, codigo o rango de empleados.</p>
            </div>

            <div class="users-form-grid users-form-grid--datos">
              <label class="tracking-field">
                <span class="input-label">Documento</span>
                <input class="input input--sm" type="text" placeholder="DNI o carnet" disabled />
              </label>

              <label class="tracking-field">
                <span class="input-label">Empleado</span>
                <input class="input input--sm" type="text" placeholder="Nombre del empleado" disabled />
              </label>
            </div>

            <div class="users-form-actions">
              <button type="button" class="btn btn--primary" disabled>
                Consultar estado
              </button>
            </div>
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
