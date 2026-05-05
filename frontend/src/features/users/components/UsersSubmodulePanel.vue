<script setup lang="ts">
import { computed, ref } from 'vue'

import type { AccessPermission, AccessRole, AccessUser, UserPayload } from '../types'

type WizardStep = { id: 'datos' | 'roles' | 'permisos' | 'resumen'; label: string }
type PermissionGroup = { moduleName: string; permissions: AccessPermission[] }
type PermissionReviewItem = { moduleName: string; permission: AccessPermission }

const pendingStatusUser = ref<AccessUser | null>(null)
const directPermissionPage = ref(1)
const directPermissionPageSize = 9
const directPermissionSearchTerm = ref('')

const props = defineProps<{
  searchTerm: string
  userRoleFilter: string
  userStatusFilter: string
  userRoleOptions: AccessRole[]
  filteredUsers: AccessUser[]
  userPaginationPage: number
  userPaginationPages: number[]
  userPaginationTotalPages: number
  userPaginationTotalItems: number
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
  roleSelectionSearchTerm: string
  filteredRoles: AccessRole[]
  rolePaginationPage: number
  rolePaginationPages: number[]
  rolePaginationTotalPages: number
  rolePaginationTotalItems: number
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
  (event: 'update:userRoleFilter', value: string): void
  (event: 'update:userStatusFilter', value: string): void
  (event: 'update:userPaginationPage', value: number): void
  (event: 'update:roleSelectionSearchTerm', value: string): void
  (event: 'update:rolePaginationPage', value: number): void
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

function updateUserRoleFilter(event: Event): void {
  emit('update:userRoleFilter', (event.target as HTMLSelectElement).value)
}

function updateUserStatusFilter(event: Event): void {
  emit('update:userStatusFilter', (event.target as HTMLSelectElement).value)
}

function updateRoleSelectionSearchTerm(event: Event): void {
  emit('update:roleSelectionSearchTerm', (event.target as HTMLInputElement).value)
}

function updateDirectPermissionSearchTerm(event: Event): void {
  directPermissionSearchTerm.value = (event.target as HTMLInputElement).value
  directPermissionPage.value = 1
}

function goToUserPage(page: number): void {
  const nextPage = Math.min(Math.max(page, 1), props.userPaginationTotalPages)
  emit('update:userPaginationPage', nextPage)
}

function goToRolePage(page: number): void {
  const nextPage = Math.min(Math.max(page, 1), props.rolePaginationTotalPages)
  emit('update:rolePaginationPage', nextPage)
}

function goToDirectPermissionPage(page: number): void {
  directPermissionPage.value = Math.min(Math.max(page, 1), directPermissionTotalPages.value)
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

function requestUserStatusToggle(user: AccessUser): void {
  if (!user.is_active) {
    emit('toggle-user-active', user)
    return
  }

  pendingStatusUser.value = user
}

function closeStatusModal(): void {
  pendingStatusUser.value = null
}

function confirmUserStatusToggle(): void {
  if (!pendingStatusUser.value) {
    return
  }

  emit('toggle-user-active', pendingStatusUser.value)
  pendingStatusUser.value = null
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

const effectivePermissionReviewItems = computed<PermissionReviewItem[]>(() =>
  props.effectivePermissionsByModule.flatMap((group) =>
    group.permissions.map((permission) => ({
      moduleName: group.moduleName,
      permission,
    })),
  ),
)

const allAvailableDirectPermissionItems = computed<PermissionReviewItem[]>(() =>
  props.availableDirectPermissionsByModule.flatMap((group) =>
    group.permissions.map((permission) => ({
      moduleName: group.moduleName,
      permission,
    })),
  ),
)

const availableDirectPermissionItems = computed<PermissionReviewItem[]>(() => {
  const query = directPermissionSearchTerm.value.trim().toLowerCase()

  if (!query) {
    return allAvailableDirectPermissionItems.value
  }

  return allAvailableDirectPermissionItems.value.filter((item) => {
    const permission = item.permission
    return [permission.nombre, permission.codigo, permission.modulo, permission.accion, permission.descripcion, item.moduleName]
      .join(' ')
      .toLowerCase()
      .includes(query)
  })
})

const directPermissionTotalPages = computed(() =>
  Math.max(1, Math.ceil(availableDirectPermissionItems.value.length / directPermissionPageSize)),
)

const directPermissionPages = computed(() =>
  Array.from({ length: directPermissionTotalPages.value }, (_, index) => index + 1),
)

const paginatedDirectPermissionItems = computed(() => {
  if (directPermissionPage.value > directPermissionTotalPages.value) {
    directPermissionPage.value = directPermissionTotalPages.value
  }

  const start = (directPermissionPage.value - 1) * directPermissionPageSize
  return availableDirectPermissionItems.value.slice(start, start + directPermissionPageSize)
})

</script>

<template>
  <section v-if="!isUserWizard" class="users-list-layout">
    <section class="card card--acrylic tracking-card users-table-card" aria-label="Listado de usuarios">
      <div class="card__body users-table-body">
        <div class="users-filter-row">
          <div class="tracking-field users-filter-search">
            <span class="input-label">Buscar usuario</span>
            <label class="search-input search-input--sm" aria-label="Buscar usuario">
              <span class="search-input__icon" aria-hidden="true">
                <svg viewBox="0 0 16 16" fill="none">
                  <path d="M7.25 12.25A5 5 0 1 0 7.25 2.25a5 5 0 0 0 0 10ZM11 11l3 3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
                </svg>
              </span>
              <input
                :value="searchTerm"
                class="search-input__field"
                type="text"
                placeholder="Usuario, nombre, correo o area"
                @input="updateSearchTerm"
              />
            </label>
          </div>

          <label class="tracking-field">
            <span class="input-label">Rol</span>
            <select :value="userRoleFilter" class="select select--sm" @change="updateUserRoleFilter">
              <option value="">Todos los roles</option>
              <option v-for="role in userRoleOptions" :key="role.id" :value="role.id">{{ role.nombre }}</option>
            </select>
          </label>

          <label class="tracking-field">
            <span class="input-label">Estado</span>
            <select :value="userStatusFilter" class="select select--sm" @change="updateUserStatusFilter">
              <option value="">Todos los estados</option>
              <option value="active">Activos</option>
              <option value="inactive">Inactivos</option>
            </select>
          </label>
        </div>

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

        <div class="users-table-footer">
          <nav v-if="userPaginationTotalItems > 0" class="pagination pagination--sm users-pagination" aria-label="Paginacion de usuarios">
            <button
              type="button"
              class="btn btn--ghost btn--sm"
              :disabled="userPaginationPage === 1"
              @click="goToUserPage(userPaginationPage - 1)"
            >
              Anterior
            </button>

            <button
              v-for="page in userPaginationPages"
              :key="`users-page-${page}`"
              type="button"
              class="btn btn--sm"
              :class="page === userPaginationPage ? 'btn--primary' : 'btn--ghost'"
              :aria-current="page === userPaginationPage ? 'page' : undefined"
              @click="goToUserPage(page)"
            >
              {{ page }}
            </button>

            <button
              type="button"
              class="btn btn--ghost btn--sm"
              :disabled="userPaginationPage === userPaginationTotalPages"
              @click="goToUserPage(userPaginationPage + 1)"
            >
              Siguiente
            </button>
          </nav>

          <button type="button" class="btn btn--primary btn--sm users-create-button" @click="emit('create-user')">
            Nuevo usuario
          </button>
        </div>
      </div>
    </section>

    <section class="card card--acrylic tracking-card users-detail-card" aria-label="Resumen del usuario">
      <div class="card__body users-detail-body">
        <template v-if="selectedUser">
          <div class="users-detail-header">
            <p class="users-detail-name">{{ selectedUser.fullname || selectedUser.username }}</p>
            <span
              class="users-detail-status"
              :class="selectedUser.is_active ? 'users-detail-status--active' : 'users-detail-status--inactive'"
              :title="selectedUser.is_active ? 'Activo' : 'Inactivo'"
            >
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
                <span v-if="selectedUser.area" class="badge badge--info">{{ selectedUser.area }}</span>
                <span v-else class="users-detail-value">-</span>
              </span>
            </article>
            <article class="users-detail-item">
              <span class="users-detail-label">Roles</span>
              <span class="users-detail-badges">
                <span
                  v-for="roleLabel in getUserRoleBadges(selectedUser)"
                  :key="`${selectedUser.id}-detail-${roleLabel}`"
                  class="badge badge--secondary"
                >
                  {{ roleLabel }}
                </span>
                <span v-if="getUserRoleBadges(selectedUser).length === 0" class="users-detail-value">Sin roles</span>
              </span>
            </article>
          </div>

          <div class="users-detail-actions">
            <button type="button" class="btn btn--primary btn--sm" @click="emit('edit-user', selectedUser)">Editar</button>
            <button
              type="button"
              class="btn btn--ghost btn--sm"
              :class="selectedUser.is_active ? 'users-action-danger' : ''"
              @click="requestUserStatusToggle(selectedUser)"
            >
              {{ selectedUser.is_active ? 'Desactivar' : 'Activar' }}
            </button>
          </div>
        </template>

        <div v-else class="users-empty-state">
          Selecciona un usuario del listado para ver su ficha resumida.
        </div>
      </div>
    </section>

    <div v-if="pendingStatusUser" class="modal-overlay modal-overlay--open">
      <section class="modal modal--danger" role="dialog" aria-modal="true" aria-labelledby="users-disable-title">
        <header class="modal__header">
          <p id="users-disable-title" class="modal__title">Deshabilitar usuario</p>
          <button type="button" class="modal__close" aria-label="Cerrar" @click="closeStatusModal">
            <span aria-hidden="true">×</span>
          </button>
        </header>

        <div class="modal__body">
          <p>
            Se deshabilitara a <strong>{{ pendingStatusUser.fullname || pendingStatusUser.username }}</strong>.
            El usuario no deberia poder operar hasta que sea activado nuevamente.
          </p>
        </div>

        <footer class="modal__footer">
          <button type="button" class="btn btn--outline btn--sm" @click="closeStatusModal">Cancelar</button>
          <button type="button" class="btn btn--danger btn--sm" @click="confirmUserStatusToggle">Deshabilitar</button>
        </footer>
      </section>
    </div>
  </section>

  <section v-else class="card card--acrylic tracking-card users-wizard-card" aria-label="Flujo de usuario">
    <div class="card__body users-wizard-body">
      <div class="users-stage-header">
        <span class="badge badge--info badge--pill">Paso {{ currentWizardStepIndex + 1 }} de {{ userWizardSteps.length }}</span>
      </div>

      <div
        class="phase-stepper"
        :class="`phase-stepper--step-${currentWizardStepIndex}`"
        aria-label="Etapas del flujo de usuario"
      >
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
            <p class="users-access-title users-access-title--inline">
              Datos base:
              <span class="users-access-copy">Completa la informacion principal del usuario antes de definir accesos.</span>
            </p>
          </div>

          <div class="users-form-grid users-form-grid--datos">
            <label class="tracking-field">
              <span class="input-label">Username</span>
              <input
                v-model="form.username"
                class="input input--sm"
                :class="{ 'input--error': userValidationAttempted && userFormErrors.username }"
                type="text"
                placeholder="usuario.sigemo"
              />
            </label>

            <label class="tracking-field">
              <span class="input-label">{{ formMode === 'create' ? 'Contrasena' : 'Nueva contrasena' }}</span>
              <input
                v-model="form.password_hash"
                class="input input--sm"
                type="text"
                :placeholder="formMode === 'create' ? 'Si no ingresas, se usara el username' : 'Opcional para mantener la actual'"
              />
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
            </label>
          </div>

          <label class="users-toggle toggle toggle--success">
            <input v-model="form.is_active" class="toggle__input" type="checkbox" />
            <span class="toggle__track" aria-hidden="true">
              <span class="toggle__thumb" />
            </span>
            <span class="toggle__label">Usuario activo</span>
          </label>
        </section>
      </div>

      <div v-else-if="userStep === 'roles'" class="users-form-body">
        <section class="users-access-panel users-access-panel--summary users-access-panel--summary-inline">
          <div class="users-access-header">
            <p class="users-access-title users-access-title--inline">
              Roles del usuario:
              <span class="users-access-copy">Selecciona los roles base que definiran el acceso heredado del usuario.</span>
            </p>
          </div>

          <div class="users-access-summary-strip">
            <article class="users-access-summary-card users-access-summary-card--compact">
              <span class="users-access-summary-value">{{ selectedFormRoles.length }}</span>
              <span class="users-access-summary-label">Roles base</span>
            </article>
            <article class="users-access-summary-card users-access-summary-card--compact">
              <span class="users-access-summary-value">{{ inheritedPermissionIds.length }}</span>
              <span class="users-access-summary-label">Permisos heredados</span>
            </article>
          </div>
        </section>

        <section class="users-access-panel">
          <div class="users-access-header users-access-header--toolbar">
            <div>
              <p class="users-access-title">Seleccion de roles</p>
              <p class="users-access-copy">Puedes asignar uno o varios roles segun el alcance operativo del usuario.</p>
            </div>

            <label class="search-input search-input--sm users-selection-search" aria-label="Buscar roles">
              <span class="search-input__icon" aria-hidden="true">
                <svg viewBox="0 0 16 16" fill="none">
                  <path d="M7.25 12.25A5 5 0 1 0 7.25 2.25a5 5 0 0 0 0 10ZM11 11l3 3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
                </svg>
              </span>
              <input
                :value="roleSelectionSearchTerm"
                class="search-input__field"
                type="text"
                placeholder="Buscar rol"
                @input="updateRoleSelectionSearchTerm"
              />
            </label>
          </div>

          <div class="users-role-selector-grid">
            <label
              v-for="role in filteredRoles"
              :key="role.id"
              class="users-role-choice checkbox"
              :class="{ 'users-role-choice--active': form.role_ids.includes(role.id) }"
            >
              <input
                :checked="form.role_ids.includes(role.id)"
                class="checkbox__input"
                type="checkbox"
                @change="toggleFormRole(role.id)"
              />
              <span class="checkbox__box" aria-hidden="true" />
              <span class="users-role-choice-copy">
                <span class="users-role-choice-heading">
                  <span class="users-role-choice-name">{{ role.nombre }}</span>
                  <span class="users-role-choice-status" :class="role.estado ? 'users-role-choice-status--active' : 'users-role-choice-status--inactive'">
                    <span class="status-dot" :class="role.estado ? '' : 'status-dot--offline'" aria-hidden="true" />
                    <span>{{ role.estado ? 'Activo' : 'Inactivo' }}</span>
                  </span>
                </span>
                <span class="users-role-choice-meta">{{ role.codigo }}</span>
                <span v-if="role.descripcion" class="users-role-choice-description">{{ role.descripcion }}</span>
                <span class="users-role-choice-tags">
                  <span class="badge badge--sm badge--info">
                    {{ role.permission_ids.length }} permiso{{ role.permission_ids.length === 1 ? '' : 's' }}
                  </span>
                  <span class="badge badge--sm badge--secondary users-role-user-count" :title="`${role.user_ids.length} usuario${role.user_ids.length === 1 ? '' : 's'}`">
                    <svg viewBox="0 0 16 16" fill="none" aria-hidden="true">
                      <path
                        d="M8 8.2A2.85 2.85 0 1 0 8 2.5a2.85 2.85 0 0 0 0 5.7Zm0 1.55c-2.56 0-4.64 1.4-4.64 3.12v.63h9.28v-.63c0-1.72-2.08-3.12-4.64-3.12Z"
                        fill="currentColor"
                      />
                    </svg>
                    <span>{{ role.user_ids.length }}</span>
                  </span>
                </span>
              </span>
            </label>
          </div>

          <nav v-if="rolePaginationTotalItems > 0" class="pagination pagination--sm users-pagination users-pagination--roles" aria-label="Paginacion de roles">
            <button
              type="button"
              class="btn btn--ghost btn--sm"
              :disabled="rolePaginationPage === 1"
              @click="goToRolePage(rolePaginationPage - 1)"
            >
              Anterior
            </button>

            <button
              v-for="page in rolePaginationPages"
              :key="`roles-page-${page}`"
              type="button"
              class="btn btn--sm"
              :class="page === rolePaginationPage ? 'btn--primary' : 'btn--ghost'"
              :aria-current="page === rolePaginationPage ? 'page' : undefined"
              @click="goToRolePage(page)"
            >
              {{ page }}
            </button>

            <button
              type="button"
              class="btn btn--ghost btn--sm"
              :disabled="rolePaginationPage === rolePaginationTotalPages"
              @click="goToRolePage(rolePaginationPage + 1)"
            >
              Siguiente
            </button>
          </nav>
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
          <div class="users-access-header users-access-header--toolbar">
            <div>
              <p class="users-access-title">Seleccion de permisos</p>
              <p class="users-access-copy">Solo se muestran permisos que todavia no vienen heredados desde roles.</p>
            </div>

            <label class="search-input search-input--sm users-selection-search" aria-label="Buscar permisos">
              <span class="search-input__icon" aria-hidden="true">
                <svg viewBox="0 0 16 16" fill="none">
                  <path d="M7.25 12.25A5 5 0 1 0 7.25 2.25a5 5 0 0 0 0 10ZM11 11l3 3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
                </svg>
              </span>
              <input
                :value="directPermissionSearchTerm"
                class="search-input__field"
                type="text"
                placeholder="Buscar permiso"
                @input="updateDirectPermissionSearchTerm"
              />
            </label>
          </div>

          <div class="users-role-selector-grid">
            <label
              v-for="item in paginatedDirectPermissionItems"
              :key="item.permission.id"
              class="users-permission-choice checkbox"
              :class="{ 'users-permission-choice--active': directPermissionIds.includes(item.permission.id) }"
            >
              <input
                :checked="directPermissionIds.includes(item.permission.id)"
                class="checkbox__input"
                type="checkbox"
                @change="toggleFormPermission(item.permission.id)"
              />
              <span class="checkbox__box" aria-hidden="true" />
              <span class="users-permission-choice-copy">
                <span class="users-permission-choice-heading">
                  <span class="users-permission-choice-title-row">
                    <span class="users-permission-choice-name">{{ item.permission.nombre }}</span>
                    <span class="users-chip-meta">{{ item.permission.codigo }}</span>
                  </span>
                  <span
                    class="users-role-choice-status"
                    :class="item.permission.estado ? 'users-role-choice-status--active' : 'users-role-choice-status--inactive'"
                  >
                    <span class="status-dot" :class="item.permission.estado ? '' : 'status-dot--offline'" aria-hidden="true" />
                    <span>{{ item.permission.estado ? 'Activo' : 'Inactivo' }}</span>
                  </span>
                </span>
                <span v-if="item.permission.descripcion" class="users-role-choice-description">{{ item.permission.descripcion }}</span>
                <span class="users-role-choice-tags">
                  <span class="badge badge--sm badge--info">{{ item.moduleName }}</span>
                  <span v-if="item.permission.accion" class="badge badge--sm badge--secondary">{{ item.permission.accion }}</span>
                </span>
              </span>
            </label>

            <p v-if="availableDirectPermissionItems.length === 0" class="users-empty-state users-selector-empty">
              No hay permisos directos disponibles para seleccionar.
            </p>
          </div>

          <nav
            v-if="availableDirectPermissionItems.length > 0"
            class="pagination pagination--sm users-pagination users-pagination--roles users-tab-pagination"
            aria-label="Paginacion de permisos directos"
          >
            <button
              type="button"
              class="btn btn--ghost btn--sm"
              :disabled="directPermissionPage === 1"
              @click="goToDirectPermissionPage(directPermissionPage - 1)"
            >
              Anterior
            </button>

            <button
              v-for="page in directPermissionPages"
              :key="`direct-permission-page-${page}`"
              type="button"
              class="btn btn--sm"
              :class="page === directPermissionPage ? 'btn--primary' : 'btn--ghost'"
              :aria-current="page === directPermissionPage ? 'page' : undefined"
              @click="goToDirectPermissionPage(page)"
            >
              {{ page }}
            </button>

            <button
              type="button"
              class="btn btn--ghost btn--sm"
              :disabled="directPermissionPage === directPermissionTotalPages"
              @click="goToDirectPermissionPage(directPermissionPage + 1)"
            >
              Siguiente
            </button>
          </nav>
        </section>
      </div>

      <div v-else class="users-form-body users-review-body">
        <section class="users-review-overview">
          <div class="users-review-user">
            <span class="users-review-kicker">Confirmacion</span>
            <span class="users-review-name-row">
              <span class="users-review-name">{{ [form.name, form.last_name].filter(Boolean).join(' ') || form.username || '-' }}</span>
              <span v-for="role in selectedFormRoles" :key="`review-role-${role.id}`" class="badge badge--secondary">
                {{ role.nombre }}
              </span>
            </span>

            <span class="users-review-tags">
              <span class="users-review-tag">
                <span>Username</span>
                <strong>{{ form.username || '-' }}</strong>
              </span>
              <span class="users-review-tag">
                <span>Correo</span>
                <strong>{{ form.email || '-' }}</strong>
              </span>
              <span class="users-review-tag">
                <span>Area</span>
                <strong>{{ form.area || '-' }}</strong>
              </span>
              <span class="users-review-tag">
                <span>Acceso</span>
                <strong>
                  {{ selectedFormRoles.length }} rol{{ selectedFormRoles.length === 1 ? '' : 'es' }} /
                  {{ effectivePermissionIdsPreview.length }} permiso{{ effectivePermissionIdsPreview.length === 1 ? '' : 's' }}
                </strong>
              </span>
            </span>
          </div>
        </section>

        <section class="users-access-panel users-review-permissions">
          <div class="users-access-header">
            <p class="users-access-title">Permisos efectivos</p>
          </div>

          <div v-if="effectivePermissionIdsPreview.length === 0" class="users-empty-state">
            Aun no hay permisos efectivos asignados para este usuario.
          </div>

          <div class="users-review-chip-grid">
            <article
              v-for="item in effectivePermissionReviewItems"
              :key="item.permission.id"
              class="users-permission-choice users-permission-choice--readonly"
            >
              <span class="users-permission-choice-copy">
                <span class="users-permission-choice-heading">
                  <span class="users-permission-choice-title-row">
                    <span class="users-permission-choice-name">{{ item.permission.nombre }}</span>
                    <span class="users-chip-meta">{{ item.permission.codigo }}</span>
                  </span>
                  <span class="badge badge--sm" :class="inheritedPermissionIds.includes(item.permission.id) ? 'badge--info' : 'badge--secondary'">
                    {{ inheritedPermissionIds.includes(item.permission.id) ? 'Heredado' : 'Directo' }}
                  </span>
                </span>
                <span v-if="item.permission.descripcion" class="users-role-choice-description">{{ item.permission.descripcion }}</span>
                <span class="users-role-choice-tags">
                  <span class="badge badge--sm badge--info">{{ item.moduleName }}</span>
                  <span v-if="item.permission.accion" class="badge badge--sm badge--secondary">{{ item.permission.accion }}</span>
                </span>
              </span>
            </article>
          </div>
        </section>
      </div>

      <div class="users-form-actions">
        <button
          v-if="currentWizardStepIndex > 0"
          type="button"
          class="btn btn--ghost users-action-danger"
          @click="emit('cancel-user-wizard')"
        >
          Cancelar
        </button>
        <button
          type="button"
          class="btn"
          :class="currentWizardStepIndex === 0 ? 'btn--ghost users-action-danger' : 'btn--ghost'"
          @click="emit('previous-wizard-step')"
        >
          {{ wizardSecondaryLabel }}
        </button>
        <button type="button" class="btn btn--primary" :disabled="isSavingUser" @click="emit('primary-wizard-action')">
          {{ wizardPrimaryLabel }}
        </button>
      </div>
    </div>
  </section>
</template>
