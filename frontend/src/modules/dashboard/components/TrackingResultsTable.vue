<script setup lang="ts">
import type { TrackingRow } from '../types'

defineProps<{
  rows: TrackingRow[]
  canViewDetail: boolean
}>()
</script>

<template>
  <section class="card card--acrylic tracking-card tracking-results" aria-label="Resultados de seguimiento">
    <header class="card__header tracking-card-header--space-between">
      <p class="card__header-title tracking-card-title">
        <svg viewBox="0 0 24 24" fill="none" class="tracking-card-title-icon" aria-hidden="true">
          <path d="M7 3H17V7H7V3 Z M7 11H17V21H7V11 Z" stroke="currentColor" stroke-width="1.8" />
        </svg>
        RESULTADOS DE SEGUIMIENTO
      </p>

      <div class="toolbar toolbar--flush tracking-toolbar" aria-label="Acciones rapidas">
        <button type="button" class="icon-btn icon-btn--ghost" aria-label="Descargar">
          <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path d="M12 4V14 M8 10L12 14L16 10 M5 19H19" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
        </button>
        <button type="button" class="icon-btn icon-btn--ghost" aria-label="Actualizar">
          <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path d="M20 11A8 8 0 1 0 18.4 16 M20 11V5 M20 11H14" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" />
          </svg>
        </button>
      </div>
    </header>

    <div class="card__body tracking-table-wrap">
      <table class="table table--compact table--hoverable tracking-table tracking-table--borderless">
        <thead>
          <tr>
            <th>Nro. Documento</th>
            <th>Nombres</th>
            <th>Unidad</th>
            <th>Puesto</th>
            <th>Estado</th>
            <th>Dias Vigencia</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in rows" :key="row.id">
            <td>{{ row.documentNumber }}</td>
            <td>{{ row.fullName }}</td>
            <td>{{ row.unit }}</td>
            <td>{{ row.position }}</td>
            <td>
              <span
                class="badge badge--sm"
                :class="{
                  'badge--success': row.status === 'Vigente',
                  'badge--warning': row.status === 'Por vencer',
                  'badge--danger': row.status === 'Vencido',
                }"
              >
                {{ row.status }}
              </span>
            </td>
            <td>{{ row.daysRemaining }}</td>
            <td>
              <button v-if="canViewDetail" type="button" class="icon-btn icon-btn--ghost" aria-label="Ver detalle">
                <svg viewBox="0 0 24 24" fill="none" aria-hidden="true">
                  <path d="M2 12C3.75 8.5 7.34 6 12 6C16.66 6 20.25 8.5 22 12C20.25 15.5 16.66 18 12 18C7.34 18 3.75 15.5 2 12 Z" stroke="currentColor" stroke-width="1.8" />
                  <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="1.8" />
                </svg>
              </button>
              <span v-else class="tracking-eye-disabled">-</span>
            </td>
          </tr>
          <tr v-if="rows.length === 0">
            <td colspan="7" class="tracking-empty">Sin resultados para los filtros seleccionados.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>
