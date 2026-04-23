<script setup lang="ts">
import { computed, ref } from 'vue'

import AppShell from '@/modules/app-shell/components/AppShell.vue'
import AppSidebar from '@/modules/app-shell/components/AppSidebar.vue'
import TrackingFiltersPanel from '@/modules/dashboard/components/TrackingFiltersPanel.vue'
import TrackingPageHeader from '@/modules/dashboard/components/TrackingPageHeader.vue'
import TrackingResultsTable from '@/modules/dashboard/components/TrackingResultsTable.vue'
import { mockTrackingRows } from '@/modules/dashboard/mock/trackingRows'
import type { TrackingFilters } from '@/modules/dashboard/types'

interface UserSession {
  rol_id?: string | number
  role?: string
}

const rolesWithDetailAccess = new Set(['ADMIN', 'SUPERVISOR', 'RRHH'])

const appliedFilters = ref<TrackingFilters>({
  documentNumber: '',
  status: 'Todos',
  unit: '',
  recruiter: '',
})

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
</script>

<template>
  <AppShell>
    <template #sidebar>
      <AppSidebar />
    </template>

    <section class="tracking-page" aria-label="Vista principal de seguimiento">
      <TrackingPageHeader section="EMOS" page-title="SEGUIMIENTO EMO'S" />
      <TrackingFiltersPanel @apply="handleApplyFilters" />
      <TrackingResultsTable :rows="filteredRows" :can-view-detail="canViewDetail" />
    </section>
  </AppShell>
</template>
