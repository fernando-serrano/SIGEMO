<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

import TrackingFiltersPanel from '@/features/dashboard/components/TrackingFiltersPanel.vue'
import TrackingPageHeader from '@/features/dashboard/components/TrackingPageHeader.vue'
import TrackingResultsTable from '@/features/dashboard/components/TrackingResultsTable.vue'
import { mockTrackingRows } from '@/features/dashboard/mock/trackingRows'
import AppSidebar from '@/features/navigation/components/AppSidebar.vue'
import type { TrackingFilters } from '@/features/dashboard/types'
import AppShell from '@/shared/layouts/AppShell.vue'

interface UserSession {
  rol_id?: string | number
  role?: string
}

const rolesWithDetailAccess = new Set(['ADMIN', 'SUPERVISOR', 'RRHH'])
const mobileBreakpoint = window.matchMedia('(max-width: 1080px)')

const appliedFilters = ref<TrackingFilters>({
  documentNumber: '',
  status: 'Todos',
  unit: '',
  recruiter: '',
})
const isSidebarOpen = ref(false)

const canViewDetail = computed(() => {
  const raw = sessionStorage.getItem('sigemo-user')

  if (!raw) {
    return true
  }

  try {
    const parsed = JSON.parse(raw) as UserSession
    const roleValue = String(parsed.role ?? parsed.rol_id ?? '').trim().toUpperCase()

    if (!roleValue) {
      return true
    }

    return rolesWithDetailAccess.has(roleValue)
  } catch {
    return true
  }
})

const filteredRows = computed(() => {
  const byDocument = appliedFilters.value.documentNumber.toLowerCase()
  const byStatus = appliedFilters.value.status
  const byUnit = appliedFilters.value.unit.toLowerCase()
  const byRecruiter = appliedFilters.value.recruiter.toLowerCase()

  return mockTrackingRows.filter((row) => {
    const documentMatch = !byDocument || row.documentNumber.toLowerCase().includes(byDocument)
    const statusMatch = byStatus === 'Todos' || row.status === byStatus
    const unitMatch = !byUnit || row.unit.toLowerCase().includes(byUnit)
    const recruiterMatch = !byRecruiter || row.fullName.toLowerCase().includes(byRecruiter)

    return documentMatch && statusMatch && unitMatch && recruiterMatch
  })
})

function handleApplyFilters(filters: TrackingFilters): void {
  appliedFilters.value = filters
}

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

    <section class="tracking-page" aria-label="Vista principal de seguimiento">
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

      <TrackingPageHeader section="EMOS" page-title="SEGUIMIENTO EMO'S" />
      <TrackingFiltersPanel @apply="handleApplyFilters" />
      <TrackingResultsTable :rows="filteredRows" :can-view-detail="canViewDetail" />
    </section>
  </AppShell>
</template>
