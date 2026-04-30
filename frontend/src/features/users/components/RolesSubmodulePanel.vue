<script setup lang="ts">
import type { AccessPermission, AccessRole, AccessUser, RolePayload } from '../types'

type PermissionGroup = { moduleName: string; permissions: AccessPermission[] }

const props = defineProps<{
  roleSearchTerm: string
  filteredRoles: AccessRole[]
  selectedRoleId: string | null
  roleFormMode: 'create' | 'edit'
  roleForm: RolePayload
  sortedUsers: AccessUser[]
  permissionsByModule: PermissionGroup[]
  roleFeedback: string
  roleFeedbackTone: 'success' | 'warning' | 'danger' | 'accent'
  roleValidationAttempted: boolean
  roleFormErrors: Record<'codigo' | 'nombre', string>
  isSavingRole: boolean
}>()

const emit = defineEmits<{
  (event: 'update:roleSearchTerm', value: string): void
  (event: 'select-role', role: AccessRole): void
  (event: 'create-role'): void
  (event: 'save-role'): void
}>()

function updateRoleSearchTerm(event: Event): void {
  emit('update:roleSearchTerm', (event.target as HTMLInputElement).value)
}

function toggleSelection(collection: string[], value: string): string[] {
  return collection.includes(value) ? collection.filter((item) => item !== value) : [...collection, value]
}

function toggleRolePermission(permissionId: string): void {
  props.roleForm.permission_ids = toggleSelection(props.roleForm.permission_ids, permissionId)
}

function toggleRoleUser(userId: string): void {
  props.roleForm.user_ids = toggleSelection(props.roleForm.user_ids, userId)
}
</script>

<template>
  <div class="users-role-layout">
    <section class="card card--acrylic tracking-card users-role-list-card" aria-label="Listado de roles">
      <header class="card__header tracking-card-header--space-between">
        <div>
          <p class="card__header-title tracking-card-title">ROLES</p>
          <p class="users-card-copy">Crea, edita y asigna roles a usuarios concretos.</p>
        </div>

        <button type="button" class="btn btn--primary btn--sm" @click="emit('create-role')">
          Nuevo rol
        </button>
      </header>

      <div class="card__body users-role-list">
        <label class="tracking-field">
          <span class="input-label">Buscar rol</span>
          <input :value="roleSearchTerm" class="input input--sm" type="text" placeholder="Codigo, nombre o descripcion" @input="updateRoleSearchTerm" />
        </label>

        <button
          v-for="role in filteredRoles"
          :key="role.id"
          type="button"
          class="users-role-item"
          :class="{ 'users-role-item--active': selectedRoleId === role.id }"
          @click="emit('select-role', role)"
        >
          <span class="users-role-item-name">{{ role.nombre }}</span>
          <span class="users-role-item-code">{{ role.codigo }}</span>
        </button>
      </div>
    </section>

    <section class="card card--acrylic tracking-card users-role-card" aria-label="Formulario de rol">
      <header class="card__header tracking-card-header--space-between">
        <div>
          <p class="card__header-title tracking-card-title">
            {{ roleFormMode === 'create' ? 'NUEVO ROL' : 'EDITAR ROL' }}
          </p>
          <p class="users-card-copy">Define el rol, sus permisos base y los usuarios que lo heredan.</p>
        </div>

        <button type="button" class="btn btn--ghost btn--sm" @click="emit('create-role')">
          Limpiar
        </button>
      </header>

      <div class="card__body users-role-body">
        <div class="users-form-grid">
          <label class="tracking-field">
            <span class="input-label">Codigo</span>
            <input
              v-model="roleForm.codigo"
              class="input input--sm"
              :class="{ 'input--error': roleValidationAttempted && roleFormErrors.codigo }"
              type="text"
              placeholder="ADMIN"
            />
            <span v-if="roleValidationAttempted && roleFormErrors.codigo" class="input-help input-help--error">{{ roleFormErrors.codigo }}</span>
          </label>

          <label class="tracking-field">
            <span class="input-label">Nombre</span>
            <input
              v-model="roleForm.nombre"
              class="input input--sm"
              :class="{ 'input--error': roleValidationAttempted && roleFormErrors.nombre }"
              type="text"
              placeholder="Administrador"
            />
            <span v-if="roleValidationAttempted && roleFormErrors.nombre" class="input-help input-help--error">{{ roleFormErrors.nombre }}</span>
          </label>

          <label class="tracking-field users-field-span-2">
            <span class="input-label">Descripcion</span>
            <input v-model="roleForm.descripcion" class="input input--sm" type="text" placeholder="Rol con acceso amplio al modulo" />
          </label>
        </div>

        <label class="users-toggle">
          <input v-model="roleForm.estado" type="checkbox" />
          <span>Rol activo</span>
        </label>

        <section class="users-access-panel users-access-panel--summary">
          <div class="users-access-header">
            <p class="users-access-title">Resumen del rol</p>
            <p class="users-access-copy">Controla a quienes aplica el rol y que permisos base heredan.</p>
          </div>

          <div class="users-access-summary-grid">
            <article class="users-access-summary-card">
              <span class="users-access-summary-value">{{ roleForm.user_ids.length }}</span>
              <span class="users-access-summary-label">Usuarios asociados</span>
            </article>
            <article class="users-access-summary-card">
              <span class="users-access-summary-value">{{ roleForm.permission_ids.length }}</span>
              <span class="users-access-summary-label">Permisos base</span>
            </article>
            <article class="users-access-summary-card">
              <span class="users-access-summary-value">{{ roleForm.estado ? 'ON' : 'OFF' }}</span>
              <span class="users-access-summary-label">Estado</span>
            </article>
            <article class="users-access-summary-card">
              <span class="users-access-summary-value">{{ roleFormMode === 'create' ? 'NEW' : 'EDIT' }}</span>
              <span class="users-access-summary-label">Modo</span>
            </article>
          </div>
        </section>

        <section class="users-access-panel">
          <div class="users-access-header">
            <p class="users-access-title">Usuarios del rol</p>
            <p class="users-access-copy">Asigna este rol directamente a los usuarios que deban heredarlo.</p>
          </div>

          <div class="users-selector-grid">
            <label
              v-for="user in sortedUsers"
              :key="user.id"
              class="users-role-choice"
              :class="{ 'users-role-choice--active': roleForm.user_ids.includes(user.id) }"
            >
              <input :checked="roleForm.user_ids.includes(user.id)" type="checkbox" @change="toggleRoleUser(user.id)" />
              <span class="users-role-choice-copy">
                <span class="users-role-choice-name">{{ user.fullname || user.username }}</span>
                <span class="users-role-choice-meta">{{ user.username }}</span>
              </span>
            </label>
          </div>
        </section>

        <section class="users-access-panel">
          <div class="users-access-header">
            <p class="users-access-title">Permisos base del rol</p>
            <p class="users-access-copy">Estos permisos se heredaran automaticamente a cada usuario asociado.</p>
          </div>

          <div class="users-permission-groups">
            <section v-for="group in permissionsByModule" :key="group.moduleName" class="users-permission-group">
              <header class="users-permission-group-header">
                <p class="users-permission-group-title">{{ group.moduleName }}</p>
              </header>

              <div class="users-chip-grid">
                <label v-for="permission in group.permissions" :key="permission.id" class="users-chip">
                  <input
                    :checked="roleForm.permission_ids.includes(permission.id)"
                    type="checkbox"
                    @change="toggleRolePermission(permission.id)"
                  />
                  <span class="users-chip-copy">
                    <span>{{ permission.nombre }}</span>
                    <span class="users-chip-meta">{{ permission.codigo }}</span>
                  </span>
                </label>
              </div>
            </section>
          </div>
        </section>

        <div v-if="roleFeedback" class="alert" :class="`alert--${roleFeedbackTone}`" role="alert">
          <div class="alert__icon" aria-hidden="true">
            <span v-if="roleFeedbackTone === 'success'">✓</span>
            <span v-else-if="roleFeedbackTone === 'warning'">!</span>
            <span v-else-if="roleFeedbackTone === 'danger'">×</span>
            <span v-else>i</span>
          </div>
          <div class="alert__content">
            <div class="alert__title">Validacion</div>
            <div class="alert__message">{{ roleFeedback }}</div>
          </div>
        </div>

        <div class="users-form-actions">
          <button type="button" class="btn btn--primary" :disabled="isSavingRole" @click="emit('save-role')">
            {{ isSavingRole ? 'Guardando...' : roleFormMode === 'create' ? 'Crear rol' : 'Guardar rol' }}
          </button>
        </div>
      </div>
    </section>
  </div>
</template>
