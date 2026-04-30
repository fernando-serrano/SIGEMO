<script setup lang="ts">
import type { AccessPermission, AccessRole, AccessUser, UserPayload } from '../types'

type WizardStep = { id: 'datos' | 'roles' | 'permisos' | 'resumen'; label: string }
type PermissionGroup = { moduleName: string; permissions: AccessPermission[] }

const props = defineProps<{
  searchTerm: string
  filteredUsers: AccessUser[]
  selectedUserId: string | null
  selectedUser: AccessUser | null
  isUserWizard: boolean
  wizardTitle: string
  currentWizardStepIndex: number
  userWizardSteps: readonly WizardStep[]
  userStep: WizardStep['id']
  userViewMode: 'list' | 'create' | 'edit'
  formMode: 'create' | 'edit'
  form: UserPayload
  selectedFormRoles: AccessRole[]
  filteredRoles: AccessRole[]
  inheritedPermissionIds: string[]
  directPermissionIds: string[]
  effectivePermissionIdsPreview: string[]
  availableDirectPermissionsByModule: PermissionGroup[]
  effectivePermissionsByModule: PermissionGroup[]
  userFeedback: string
  userFeedbackTone: 'success' | 'warning' | 'danger' | 'accent'
  userValidationAttempted: boolean
  userFormErrors: Record<'username' | 'name' | 'last_name' | 'email' | 'area', string>
  isSavingUser: boolean
  wizardPrimaryLabel: string
  wizardSecondaryLabel: string
  describeUserRoles: (user: AccessUser) => string
  describeEffectivePermissionCount: (user: AccessUser) => string
}>()

const emit = defineEmits<{
  (event: 'update:searchTerm', value: string): void
  (event: 'create-user'): void
  (event: 'edit-user', user: AccessUser): void
  (event: 'open-user-detail', user: AccessUser): void
  (event: 'toggle-user-active', user: AccessUser): void
  (event: 'cancel-user-wizard'): void
  (event: 'previous-wizard-step'): void
  (event: 'primary-wizard-action'): void
  (event: 'goto-wizard-step', stepId: WizardStep['id']): void
}>()

function updateSearchTerm(event: Event): void {
  emit('update:searchTerm', (event.target as HTMLInputElement).value)
}

function toggleSelection(collection: string[], value: string): string[] {
  return collection.includes(value) ? collection.filter((item) => item !== value) : [...collection, value]
}

function toggleFormRole(roleId: string): void {
  props.form.role_ids = toggleSelection(props.form.role_ids, roleId)
}

function toggleFormPermission(permissionId: string): void {
  props.form.permission_ids = toggleSelection(props.form.permission_ids, permissionId)
}

function getStepMeta(stepId: WizardStep['id']): string {
  if (stepId === 'datos') return 'Informacion base'
  if (stepId === 'roles') return 'Acceso heredado'
  if (stepId === 'permisos') return 'Excepciones directas'
  return 'Confirmacion final'
}

function getUserRoleBadges(user: AccessUser | null): string[] {
  if (!user) {
    return []
  }

  return props.describeUserRoles(user)
    .split(',')
    .map((value) => value.trim())
    .filter(Boolean)
}
</script>

<template>
  <section v-if="!isUserWizard" class="users-list-layout">
    <section class="card card--acrylic tracking-card users-table-card" aria-label="Listado de usuarios">
      <header class="card__header tracking-card-header--space-between">
        <div>
          <p class="card__header-title tracking-card-title">USUARIOS</p>
          <p class="users-card-copy">Vista compacta para revisar usuarios activos, roles y acciones rapidas.</p>
        </div>

        <button type="button" class="btn btn--primary btn--sm" @click="emit('create-user')">
          Nuevo usuario
        </button>
      </header>

      <div class="card__body users-table-body">
        <label class="tracking-field">
          <span class="input-label">Buscar usuario</span>
          <input :value="searchTerm" class="input input--sm" type="text" placeholder="Usuario, nombre, correo o area" @input="updateSearchTerm" />
        </label>

        <div class="tracking-table-wrap users-table-wrap">
          <table class="table table--compact table--hoverable tracking-table tracking-table--borderless users-table">
            <thead>
              <tr>
                <th>Usuario</th>
                <th>Nombre</th>
                <th>Correo</th>
                <th>Area</th>
                <th>Roles</th>
                <th>Accesos</th>
                <th>Estado</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="user in filteredUsers"
                :key="user.id"
                :class="{ 'users-table-row--selected': selectedUserId === user.id }"
                @click="emit('open-user-detail', user)"
              >
                <td>{{ user.username }}</td>
                <td>{{ user.fullname || '-' }}</td>
                <td class="users-table-email">{{ user.email || '-' }}</td>
                <td>
                  <span v-if="user.area" class="badge badge--sm badge--info badge--outline">{{ user.area }}</span>
                  <span v-else>-</span>
                </td>
                <td>
                  <div class="users-role-badge-list">
                    <span
                      v-for="roleLabel in getUserRoleBadges(user)"
                      :key="`${user.id}-${roleLabel}`"
                      class="badge badge--sm badge--secondary badge--outline"
                    >
                      {{ roleLabel }}
                    </span>
                    <span v-if="getUserRoleBadges(user).length === 0">Sin roles</span>
                  </div>
                </td>
                <td>{{ describeEffectivePermissionCount(user) }}</td>
                <td>
                  <span
                    class="status-indicator"
                    :class="user.is_active ? 'status-indicator--online' : 'status-indicator--offline'"
                    :title="user.is_active ? 'Activo' : 'Inactivo'"
                    :aria-label="user.is_active ? 'Activo' : 'Inactivo'"
                  >
                    {{ user.is_active ? 'Activo' : 'Inactivo' }}
                  </span>
                </td>
              </tr>
              <tr v-if="filteredUsers.length === 0">
                <td colspan="7" class="tracking-empty">No hay usuarios que coincidan con la busqueda.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <section class="card card--acrylic tracking-card users-detail-card" aria-label="Resumen del usuario">
      <div class="card__body users-detail-body">
        <template v-if="selectedUser">
          <div class="users-detail-header">
            <p class="users-detail-name">{{ selectedUser.fullname || selectedUser.username }}</p>
            <span class="users-detail-status" :title="selectedUser.is_active ? 'Activo' : 'Inactivo'">
              <span class="status-dot" :class="selectedUser.is_active ? '' : 'status-dot--offline'" aria-hidden="true" />
              <span>{{ selectedUser.is_active ? 'Activo' : 'Inactivo' }}</span>
            </span>
          </div>

          <div class="users-detail-stack">
            <article class="users-detail-item">
              <span class="users-detail-label">Username</span>
              <span class="users-detail-value users-detail-value--accent">{{ selectedUser.username }}</span>
            </article>
            <article class="users-detail-item">
              <span class="users-detail-label">Correo</span>
              <span class="users-detail-value users-detail-value--accent users-detail-value--compact users-detail-value--break">{{ selectedUser.email || '-' }}</span>
            </article>
            <article class="users-detail-item">
              <span class="users-detail-label">Area</span>
              <span class="users-detail-badges">
                <span v-if="selectedUser.area" class="badge badge--sm badge--info badge--outline">{{ selectedUser.area }}</span>
                <span v-else class="users-detail-value">-</span>
              </span>
            </article>
            <article class="users-detail-item">
              <span class="users-detail-label">Roles</span>
              <span class="users-detail-badges">
                <span
                  v-for="roleLabel in getUserRoleBadges(selectedUser)"
                  :key="`${selectedUser.id}-detail-${roleLabel}`"
                  class="badge badge--sm badge--secondary badge--outline"
                >
                  {{ roleLabel }}
                </span>
                <span v-if="getUserRoleBadges(selectedUser).length === 0" class="users-detail-value">Sin roles</span>
              </span>
            </article>
          </div>

          <div class="users-detail-actions">
            <button type="button" class="btn btn--primary" @click="emit('edit-user', selectedUser)">Editar usuario</button>
            <button type="button" class="btn btn--ghost" @click="emit('toggle-user-active', selectedUser)">
              {{ selectedUser.is_active ? 'Desactivar usuario' : 'Activar usuario' }}
            </button>
          </div>
        </template>

        <div v-else class="users-empty-state">
          Selecciona un usuario del listado para ver su ficha resumida.
        </div>
      </div>
    </section>
  </section>

  <section v-else class="card card--acrylic tracking-card users-wizard-card" aria-label="Flujo de usuario">
    <header class="card__header tracking-card-header--space-between">
      <div>
        <p class="card__header-title tracking-card-title">{{ wizardTitle }}</p>
        <p class="users-card-copy">
          Paso {{ currentWizardStepIndex + 1 }} de {{ userWizardSteps.length }} para
          {{ userViewMode === 'create' ? 'registrar' : 'actualizar' }} un usuario.
        </p>
      </div>

      <button type="button" class="btn btn--ghost btn--sm" @click="emit('cancel-user-wizard')">
        Volver al listado
      </button>
    </header>

    <div class="card__body users-wizard-body">
      <div class="users-stage-header">
        <span class="badge badge--info badge--pill">Paso {{ currentWizardStepIndex + 1 }} de {{ userWizardSteps.length }}</span>
        <span class="users-stage-copy">Flujo guiado de alta y edicion de usuario</span>
      </div>

      <div class="phase-stepper" aria-label="Etapas del flujo de usuario">
        <div
          v-for="(step, index) in userWizardSteps"
          :key="step.id"
          class="phase-step"
          :class="{
            'phase-step--active': step.id === userStep,
            'phase-step--done': index < currentWizardStepIndex,
          }"
        >
          <button
            type="button"
            class="phase-step__trigger"
            :aria-current="step.id === userStep ? 'step' : undefined"
            @click="emit('goto-wizard-step', step.id)"
          >
            <span class="phase-step__bubble">
              <svg
                v-if="index < currentWizardStepIndex"
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
                <polyline points="20 6 9 17 4 12" />
              </svg>
              <span v-else>{{ index + 1 }}</span>
            </span>
            <span class="phase-step__text">
              <span class="phase-step__label">{{ step.label }}</span>
              <span class="phase-step__meta">{{ getStepMeta(step.id) }}</span>
            </span>
          </button>
        </div>
      </div>

      <div v-if="userStep === 'datos'" class="users-form-body">
        <section class="users-access-panel">
          <div class="users-access-header">
            <p class="users-access-title">Datos base</p>
            <p class="users-access-copy">Completa la informacion principal del usuario antes de definir accesos.</p>
          </div>

          <div class="users-form-grid">
            <label class="tracking-field">
              <span class="input-label">Username</span>
              <input
                v-model="form.username"
                class="input input--sm"
                :class="{ 'input--error': userValidationAttempted && userFormErrors.username }"
                type="text"
                placeholder="usuario.sigemo"
              />
              <span v-if="userValidationAttempted && userFormErrors.username" class="input-help input-help--error">{{ userFormErrors.username }}</span>
            </label>

            <label class="tracking-field">
              <span class="input-label">{{ formMode === 'create' ? 'Contrasena' : 'Nueva contrasena' }}</span>
              <input
                v-model="form.password_hash"
                class="input input--sm"
                type="text"
                :placeholder="formMode === 'create' ? 'Si no ingresas, se usara el username' : 'Opcional para mantener la actual'"
              />
              <span class="input-help">Opcional. Si queda vacio, se usara el username.</span>
            </label>

            <label class="tracking-field">
              <span class="input-label">Nombres</span>
              <input
                v-model="form.name"
                class="input input--sm"
                :class="{ 'input--error': userValidationAttempted && userFormErrors.name }"
                type="text"
                placeholder="Fernando Jesus"
              />
              <span v-if="userValidationAttempted && userFormErrors.name" class="input-help input-help--error">{{ userFormErrors.name }}</span>
            </label>

            <label class="tracking-field">
              <span class="input-label">Apellidos</span>
              <input
                v-model="form.last_name"
                class="input input--sm"
                :class="{ 'input--error': userValidationAttempted && userFormErrors.last_name }"
                type="text"
                placeholder="Serrano Garrido"
              />
              <span v-if="userValidationAttempted && userFormErrors.last_name" class="input-help input-help--error">{{ userFormErrors.last_name }}</span>
            </label>

            <label class="tracking-field">
              <span class="input-label">Correo</span>
              <input
                v-model="form.email"
                class="input input--sm"
                :class="{ 'input--error': userValidationAttempted && userFormErrors.email }"
                type="email"
                placeholder="correo@liderman.com.pe"
              />
              <span v-if="userValidationAttempted && userFormErrors.email" class="input-help input-help--error">{{ userFormErrors.email }}</span>
            </label>

            <label class="tracking-field">
              <span class="input-label">Area</span>
              <input
                v-model="form.area"
                class="input input--sm"
                :class="{ 'input--error': userValidationAttempted && userFormErrors.area }"
                type="text"
                placeholder="Operaciones, RRHH, SSO..."
              />
              <span v-if="userValidationAttempted && userFormErrors.area" class="input-help input-help--error">{{ userFormErrors.area }}</span>
            </label>
          </div>

          <label class="users-toggle">
            <input v-model="form.is_active" type="checkbox" />
            <span>Usuario activo</span>
          </label>
        </section>
      </div>

      <div v-else-if="userStep === 'roles'" class="users-form-body">
        <section class="users-access-panel users-access-panel--summary">
          <div class="users-access-header">
            <p class="users-access-title">Roles del usuario</p>
            <p class="users-access-copy">Selecciona los roles base que definiran el acceso heredado del usuario.</p>
          </div>

          <div class="users-access-summary-grid">
            <article class="users-access-summary-card">
              <span class="users-access-summary-value">{{ selectedFormRoles.length }}</span>
              <span class="users-access-summary-label">Roles base</span>
            </article>
            <article class="users-access-summary-card">
              <span class="users-access-summary-value">{{ inheritedPermissionIds.length }}</span>
              <span class="users-access-summary-label">Permisos heredados</span>
            </article>
          </div>
        </section>

        <section class="users-access-panel">
          <div class="users-access-header">
            <p class="users-access-title">Seleccion de roles</p>
            <p class="users-access-copy">Puedes asignar uno o varios roles segun el alcance operativo del usuario.</p>
          </div>

          <div class="users-role-selector-grid">
            <label
              v-for="role in filteredRoles"
              :key="role.id"
              class="users-role-choice"
              :class="{ 'users-role-choice--active': form.role_ids.includes(role.id) }"
            >
              <input :checked="form.role_ids.includes(role.id)" type="checkbox" @change="toggleFormRole(role.id)" />
              <span class="users-role-choice-copy">
                <span class="users-role-choice-name">{{ role.nombre }}</span>
                <span class="users-role-choice-meta">{{ role.codigo }}</span>
                <span v-if="role.descripcion" class="users-role-choice-description">{{ role.descripcion }}</span>
              </span>
            </label>
          </div>
        </section>
      </div>

      <div v-else-if="userStep === 'permisos'" class="users-form-body">
        <section class="users-access-panel users-access-panel--summary">
          <div class="users-access-header">
            <p class="users-access-title">Permisos directos</p>
            <p class="users-access-copy">Agrega excepciones puntuales fuera de la herencia por rol.</p>
          </div>

          <div class="users-access-summary-grid">
            <article class="users-access-summary-card">
              <span class="users-access-summary-value">{{ inheritedPermissionIds.length }}</span>
              <span class="users-access-summary-label">Por rol</span>
            </article>
            <article class="users-access-summary-card">
              <span class="users-access-summary-value">{{ directPermissionIds.length }}</span>
              <span class="users-access-summary-label">Directos</span>
            </article>
            <article class="users-access-summary-card">
              <span class="users-access-summary-value">{{ effectivePermissionIdsPreview.length }}</span>
              <span class="users-access-summary-label">Resultado</span>
            </article>
          </div>
        </section>

        <section class="users-access-panel">
          <div class="users-access-header">
            <p class="users-access-title">Seleccion de permisos</p>
            <p class="users-access-copy">Solo se muestran permisos que todavia no vienen heredados desde roles.</p>
          </div>

          <div class="users-permission-groups">
            <section v-for="group in availableDirectPermissionsByModule" :key="group.moduleName" class="users-permission-group">
              <header class="users-permission-group-header">
                <p class="users-permission-group-title">{{ group.moduleName }}</p>
              </header>

              <div class="users-chip-grid">
                <label v-for="permission in group.permissions" :key="permission.id" class="users-chip">
                  <input
                    :checked="directPermissionIds.includes(permission.id)"
                    type="checkbox"
                    @change="toggleFormPermission(permission.id)"
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
      </div>

      <div v-else class="users-form-body">
        <section class="users-access-panel users-access-panel--summary">
          <div class="users-access-header">
            <p class="users-access-title">Resumen final</p>
            <p class="users-access-copy">Antes de confirmar, revisa los datos, roles y permisos efectivos del usuario.</p>
          </div>

          <div class="users-access-summary-grid">
            <article class="users-access-summary-card">
              <span class="users-access-summary-value">{{ selectedFormRoles.length }}</span>
              <span class="users-access-summary-label">Roles</span>
            </article>
            <article class="users-access-summary-card">
              <span class="users-access-summary-value">{{ inheritedPermissionIds.length }}</span>
              <span class="users-access-summary-label">Heredados</span>
            </article>
            <article class="users-access-summary-card">
              <span class="users-access-summary-value">{{ directPermissionIds.length }}</span>
              <span class="users-access-summary-label">Directos</span>
            </article>
            <article class="users-access-summary-card">
              <span class="users-access-summary-value">{{ effectivePermissionIdsPreview.length }}</span>
              <span class="users-access-summary-label">Efectivos</span>
            </article>
          </div>
        </section>

        <section class="users-access-panel">
          <div class="users-access-header">
            <p class="users-access-title">Ficha del usuario</p>
          </div>

          <div class="users-detail-grid">
            <article class="users-detail-item">
              <span class="users-detail-label">Username</span>
              <span class="users-detail-value">{{ form.username || '-' }}</span>
            </article>
            <article class="users-detail-item">
              <span class="users-detail-label">Nombre completo</span>
              <span class="users-detail-value">{{ [form.name, form.last_name].filter(Boolean).join(' ') || '-' }}</span>
            </article>
            <article class="users-detail-item">
              <span class="users-detail-label">Correo</span>
              <span class="users-detail-value">{{ form.email || '-' }}</span>
            </article>
            <article class="users-detail-item">
              <span class="users-detail-label">Area</span>
              <span class="users-detail-value">{{ form.area || '-' }}</span>
            </article>
          </div>
        </section>

        <section class="users-access-panel">
          <div class="users-access-header">
            <p class="users-access-title">Permisos efectivos</p>
          </div>

          <div v-if="effectivePermissionIdsPreview.length === 0" class="users-empty-state">
            Aun no hay permisos efectivos asignados para este usuario.
          </div>

          <div class="users-permission-groups">
            <section v-for="group in effectivePermissionsByModule" :key="group.moduleName" class="users-permission-group">
              <header class="users-permission-group-header">
                <p class="users-permission-group-title">{{ group.moduleName }}</p>
              </header>

              <div class="users-chip-grid">
                <article v-for="permission in group.permissions" :key="permission.id" class="users-chip users-chip--readonly">
                  <span class="users-chip-copy">
                    <span>{{ permission.nombre }}</span>
                    <span class="users-chip-meta">{{ permission.codigo }}</span>
                  </span>
                  <span
                    class="badge badge--sm"
                    :class="inheritedPermissionIds.includes(permission.id) ? 'badge--secondary' : 'badge--info'"
                  >
                    {{ inheritedPermissionIds.includes(permission.id) ? 'Rol' : 'Directo' }}
                  </span>
                </article>
              </div>
            </section>
          </div>
        </section>
      </div>

      <div v-if="userFeedback" class="alert" :class="`alert--${userFeedbackTone}`" role="alert">
        <div class="alert__icon" aria-hidden="true">
          <span v-if="userFeedbackTone === 'success'">✓</span>
          <span v-else-if="userFeedbackTone === 'warning'">!</span>
          <span v-else-if="userFeedbackTone === 'danger'">×</span>
          <span v-else>i</span>
        </div>
        <div class="alert__content">
          <div class="alert__title">Validacion</div>
          <div class="alert__message">{{ userFeedback }}</div>
        </div>
      </div>

      <div class="users-form-actions users-form-actions--space-between">
        <button type="button" class="btn btn--ghost" @click="emit('previous-wizard-step')">
          {{ wizardSecondaryLabel }}
        </button>
        <button type="button" class="btn btn--primary" :disabled="isSavingUser" @click="emit('primary-wizard-action')">
          {{ wizardPrimaryLabel }}
        </button>
      </div>
    </div>
  </section>
</template>
