<script setup lang="ts">
import { reactive } from 'vue'

import type { TrackingFilters } from '../types'

const emit = defineEmits<{
  (event: 'apply', filters: TrackingFilters): void
}>()

const filters = reactive<TrackingFilters>({
  documentNumber: '',
  status: 'Todos',
  unit: '',
  recruiter: '',
})

function applyFilters(): void {
  emit('apply', {
    documentNumber: filters.documentNumber.trim(),
    status: filters.status,
    unit: filters.unit.trim(),
    recruiter: filters.recruiter.trim(),
  })
}
</script>

<template>
  <section class="card card--acrylic tracking-card" aria-label="Panel de filtros">
    <header class="card__header">
      <p class="card__header-title tracking-card-title">
        <svg viewBox="0 0 24 24" fill="none" class="tracking-card-title-icon" aria-hidden="true">
          <path d="M5 6H19L14 12V18L10 20V12L5 6Z" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round" />
        </svg>
        PANEL DE FILTROS
      </p>
    </header>

    <div class="card__body tracking-filters-grid">
      <label class="tracking-field">
        <span class="input-label">Nro. Documento</span>
        <input v-model="filters.documentNumber" class="input input--sm" type="text" placeholder="8 digitos" />
      </label>

      <label class="tracking-field">
        <span class="input-label">Estado</span>
        <select v-model="filters.status" class="select select--sm">
          <option value="Todos">Todos</option>
          <option value="Vigente">Vigente</option>
          <option value="Por vencer">Por vencer</option>
          <option value="Vencido">Vencido</option>
        </select>
      </label>

      <label class="tracking-field">
        <span class="input-label">Unidad</span>
        <input v-model="filters.unit" class="input input--sm" type="text" placeholder="Ej. Minera" />
      </label>

      <label class="tracking-field">
        <span class="input-label">Reclutador</span>
        <input v-model="filters.recruiter" class="input input--sm" type="text" placeholder="Nombre" />
      </label>

      <button type="button" class="btn btn--primary btn--sm tracking-action" @click="applyFilters">
        <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <path d="M11 4C14.87 4 18 7.13 18 11C18 14.87 14.87 18 11 18C7.13 18 4 14.87 4 11C4 7.13 7.13 4 11 4 Z M20 20L16.65 16.65" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
        </svg>
        FILTRAR
      </button>
    </div>
  </section>
</template>
