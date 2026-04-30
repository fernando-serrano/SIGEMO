<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'

import TrackingPageHeader from '@/features/dashboard/components/TrackingPageHeader.vue'
import AppSidebar from '@/features/navigation/components/AppSidebar.vue'
import AppShell from '@/shared/layouts/AppShell.vue'

const mobileBreakpoint = window.matchMedia('(max-width: 1080px)')
const isSidebarOpen = ref(false)

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

      <section class="card card--acrylic tracking-card" aria-label="Resumen del modulo SUCAMEC">
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
