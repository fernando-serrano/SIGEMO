<script setup lang="ts">
import type { AccessRole, AccessUser, PermissionPayload, AccessPermission } from '../types'

const props = defineProps<{
  permissionSearchTerm: string
  filteredPermissions: AccessPermission[]
  filteredRoles: AccessRole[]
  sortedUsers: AccessUser[]
  selectedPermissionId: string | null
  permissionFormMode: 'create' | 'edit'
  permissionForm: PermissionPayload
  permissionFeedback: string
  permissionFeedbackTone: 'success' | 'warning' | 'danger' | 'accent'
  permissionValidationAttempted: boolean
  permissionFormErrors: Record<'codigo' | 'nombre' | 'modulo' | 'accion', string>
  isSavingPermission: boolean
}>()

const emit = defineEmits<{
  (event: 'update:permissionSearchTerm', value: string): void
  (event: 'select-permission', permission: AccessPermission): void
  (event: 'create-permission'): void
  (event: 'save-permission'): void
}>()

function updatePermissionSearchTerm(event: Event): void {
  emit('update:permissionSearchTerm', (event.target as HTMLInputElement).value)
}

function toggleSelection(collection: string[], value: string): string[] {
  return collection.includes(value) ? collection.filter((item) => item !== value) : [...collection, value]
}

function togglePermissionRole(roleId: string): void {
  props.permissionForm.role_ids = toggleSelection(props.permissionForm.role_ids, roleId)
}

function togglePermissionUser(userId: string): void {
  props.permissionForm.user_ids = toggleSelection(props.permissionForm.user_ids, userId)
}
</script>

<template>
  <div class="users-role-layout">
    <section class="card card--acrylic tracking-card users-role-list-card" aria-label="Listado de permisos">
      <header class="card__header tracking-card-header--space-between">
        <div>
          <p class="card__header-title tracking-card-title">PERMISOS</p>
          <p class="users-card-copy">Crea permisos y define en que roles o usuarios aplican.</p>
        </div>

        <button type="button" class="btn btn--primary btn--sm" @click="emit('create-permission')">
          Nuevo permiso
        </button>
      </header>

      <div class="card__body users-role-list">
        <label class="tracking-field">
          <span class="input-label">Buscar permiso</span>
          <input
            :value="permissionSearchTerm"
            class="input input--sm"
            type="text"
            placeholder="Codigo, nombre, modulo o accion"
            @input="updatePermissionSearchTerm"
          />
        </label>

        <button
          v-for="permission in filteredPermissions"
          :key="permission.id"
          type="button"
          class="users-role-item"
          :class="{ 'users-role-item--active': selectedPermissionId === permission.id }"
          @click="emit('select-permission', permission)"
        >
          <span class="users-role-item-name">{{ permission.nombre }}</span>
          <span class="users-role-item-code">{{ permission.modulo || 'GENERAL' }} · {{ permission.codigo }}</span>
        </button>
      </div>
    </section>

    <section class="card card--acrylic tracking-card users-role-card" aria-label="Formulario de permiso">
      <header class="card__header tracking-card-header--space-between">
        <div>
          <p class="card__header-title tracking-card-title">
            {{ permissionFormMode === 'create' ? 'NUEVO PERMISO' : 'EDITAR PERMISO' }}
          </p>
          <p class="users-card-copy">Define el permiso y distribuyelo por roles o usuarios directos.</p>
        </div>

        <button type="button" class="btn btn--ghost btn--sm" @click="emit('create-permission')">
          Limpiar
        </button>
      </header>

      <div class="card__body users-role-body">
        <div class="users-form-grid">
          <label class="tracking-field">
            <span class="input-label">Codigo</span>
            <input
              v-model="permissionForm.codigo"
              class="input input--sm"
              :class="{ 'input--error': permissionValidationAttempted && permissionFormErrors.codigo }"
              type="text"
              placeholder="USR_EDIT"
            />
            <span v-if="permissionValidationAttempted && permissionFormErrors.codigo" class="input-help input-help--error">{{ permissionFormErrors.codigo }}</span>
          </label>

          <label class="tracking-field">
            <span class="input-label">Nombre</span>
            <input
              v-model="permissionForm.nombre"
              class="input input--sm"
              :class="{ 'input--error': permissionValidationAttempted && permissionFormErrors.nombre }"
              type="text"
              placeholder="Editar usuario"
            />
            <span v-if="permissionValidationAttempted && permissionFormErrors.nombre" class="input-help input-help--error">{{ permissionFormErrors.nombre }}</span>
          </label>

          <label class="tracking-field">
            <span class="input-label">Modulo</span>
            <input
              v-model="permissionForm.modulo"
              class="input input--sm"
              :class="{ 'input--error': permissionValidationAttempted && permissionFormErrors.modulo }"
              type="text"
              placeholder="Usuarios"
            />
            <span v-if="permissionValidationAttempted && permissionFormErrors.modulo" class="input-help input-help--error">{{ permissionFormErrors.modulo }}</span>
          </label>

          <label class="tracking-field">
            <span class="input-label">Accion</span>
            <input
              v-model="permissionForm.accion"
              class="input input--sm"
              :class="{ 'input--error': permissionValidationAttempted && permissionFormErrors.accion }"
              type="text"
              placeholder="update"
            />
            <span v-if="permissionValidationAttempted && permissionFormErrors.accion" class="input-help input-help--error">{{ permissionFormErrors.accion }}</span>
          </label>

          <label class="tracking-field users-field-span-2">
            <span class="input-label">Descripcion</span>
            <input
              v-model="permissionForm.descripcion"
              class="input input--sm"
              type="text"
              placeholder="Permite editar informacion base de usuarios"
            />
          </label>
        </div>

        <label class="users-toggle">
          <input v-model="permissionForm.estado" type="checkbox" />
          <span>Permiso activo</span>
        </label>

        <section class="users-access-panel users-access-panel--summary">
          <div class="users-access-header">
            <p class="users-access-title">Resumen del permiso</p>
            <p class="users-access-copy">Controla que roles lo heredan y que usuarios lo reciben en forma directa.</p>
          </div>

          <div class="users-access-summary-grid">
            <article class="users-access-summary-card">
              <span class="users-access-summary-value">{{ permissionForm.role_ids.length }}</span>
              <span class="users-access-summary-label">Roles asociados</span>
            </article>
            <article class="users-access-summary-card">
              <span class="users-access-summary-value">{{ permissionForm.user_ids.length }}</span>
              <span class="users-access-summary-label">Usuarios directos</span>
            </article>
            <article class="users-access-summary-card">
              <span class="users-access-summary-value">{{ permissionForm.estado ? 'ON' : 'OFF' }}</span>
              <span class="users-access-summary-label">Estado</span>
            </article>
            <article class="users-access-summary-card">
              <span class="users-access-summary-value">{{ permissionFormMode === 'create' ? 'NEW' : 'EDIT' }}</span>
              <span class="users-access-summary-label">Modo</span>
            </article>
          </div>
        </section>

        <section class="users-access-panel">
          <div class="users-access-header">
            <p class="users-access-title">Roles que heredan este permiso</p>
            <p class="users-access-copy">Selecciona los roles que deben incluir este permiso dentro de su base.</p>
          </div>

          <div class="users-role-selector-grid">
            <label
              v-for="role in filteredRoles"
              :key="role.id"
              class="users-role-choice"
              :class="{ 'users-role-choice--active': permissionForm.role_ids.includes(role.id) }"
            >
              <input :checked="permissionForm.role_ids.includes(role.id)" type="checkbox" @change="togglePermissionRole(role.id)" />
              <span class="users-role-choice-copy">
                <span class="users-role-choice-name">{{ role.nombre }}</span>
                <span class="users-role-choice-meta">{{ role.codigo }}</span>
              </span>
            </label>
          </div>
        </section>

        <section class="users-access-panel">
          <div class="users-access-header">
            <p class="users-access-title">Usuarios con permiso directo</p>
            <p class="users-access-copy">Usa esta seccion solo para excepciones fuera de la herencia por rol.</p>
          </div>

          <div class="users-selector-grid">
            <label
              v-for="user in sortedUsers"
              :key="user.id"
              class="users-role-choice"
              :class="{ 'users-role-choice--active': permissionForm.user_ids.includes(user.id) }"
            >
              <input :checked="permissionForm.user_ids.includes(user.id)" type="checkbox" @change="togglePermissionUser(user.id)" />
              <span class="users-role-choice-copy">
                <span class="users-role-choice-name">{{ user.fullname || user.username }}</span>
                <span class="users-role-choice-meta">{{ user.username }}</span>
              </span>
            </label>
          </div>
        </section>

        <div v-if="permissionFeedback" class="alert" :class="`alert--${permissionFeedbackTone}`" role="alert">
          <div class="alert__icon" aria-hidden="true">
            <span v-if="permissionFeedbackTone === 'success'">✓</span>
            <span v-else-if="permissionFeedbackTone === 'warning'">!</span>
            <span v-else-if="permissionFeedbackTone === 'danger'">×</span>
            <span v-else>i</span>
          </div>
          <div class="alert__content">
            <div class="alert__title">Validacion</div>
            <div class="alert__message">{{ permissionFeedback }}</div>
          </div>
        </div>

        <div class="users-form-actions">
          <button type="button" class="btn btn--primary" :disabled="isSavingPermission" @click="emit('save-permission')">
            {{ isSavingPermission ? 'Guardando...' : permissionFormMode === 'create' ? 'Crear permiso' : 'Guardar permiso' }}
          </button>
        </div>
      </div>
    </section>
  </div>
</template>
