<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import type { AccessPermission, AccessRole, AccessUser, PermissionPayload } from '../types'

type PermissionTab = 'datos' | 'roles' | 'usuarios'

const activePermissionTab = ref<PermissionTab>('datos')
const permissionListPage = ref(1)
const permissionListPageSize = 4
const permissionRolePage = ref(1)
const permissionRolePageSize = 9
const permissionUserPage = ref(1)
const permissionUserPageSize = 6
const assignmentSearchTerm = ref('')
const localSelectedPermissionId = ref<string | null>(null)

const props = defineProps<{
  permissionSearchTerm: string
  filteredPermissions: AccessPermission[]
  filteredRoles: AccessRole[]
  roleOptions: AccessRole[]
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
  permissionListPage.value = 1
}

const permissionListTotalPages = computed(() => Math.max(1, Math.ceil(props.filteredPermissions.length / permissionListPageSize)))

const permissionListPages = computed(() =>
  Array.from({ length: permissionListTotalPages.value }, (_, index) => index + 1),
)

const paginatedPermissions = computed(() => {
  if (permissionListPage.value > permissionListTotalPages.value) {
    permissionListPage.value = permissionListTotalPages.value
  }

  const start = (permissionListPage.value - 1) * permissionListPageSize
  return props.filteredPermissions.slice(start, start + permissionListPageSize)
})

const normalizedAssignmentSearch = computed(() => assignmentSearchTerm.value.trim().toLowerCase())
const currentSelectedPermissionId = computed(() => props.selectedPermissionId ?? localSelectedPermissionId.value)
const resolvedPermissionFormMode = computed<'create' | 'edit'>(() =>
  currentSelectedPermissionId.value ? 'edit' : props.permissionFormMode,
)
const roleLabelById = computed(() => {
  const labels = new Map<string, string>()
  props.roleOptions.forEach((role) => {
    labels.set(role.id, role.nombre || role.codigo)
  })
  return labels
})

const filteredPermissionRoles = computed(() => {
  const search = normalizedAssignmentSearch.value

  if (!search) {
    return props.filteredRoles
  }

  return props.filteredRoles.filter((role) =>
    [role.nombre, role.codigo, role.descripcion].join(' ').toLowerCase().includes(search),
  )
})

const filteredPermissionUsers = computed(() => {
  const search = normalizedAssignmentSearch.value

  if (!search) {
    return props.sortedUsers
  }

  return props.sortedUsers.filter((user) =>
    [user.fullname, user.username, user.area].join(' ').toLowerCase().includes(search),
  )
})

const permissionRoleTotalPages = computed(() => Math.max(1, Math.ceil(filteredPermissionRoles.value.length / permissionRolePageSize)))
const permissionRolePages = computed(() =>
  Array.from({ length: permissionRoleTotalPages.value }, (_, index) => index + 1),
)
const paginatedPermissionRoles = computed(() => {
  if (permissionRolePage.value > permissionRoleTotalPages.value) {
    permissionRolePage.value = permissionRoleTotalPages.value
  }

  const start = (permissionRolePage.value - 1) * permissionRolePageSize
  return filteredPermissionRoles.value.slice(start, start + permissionRolePageSize)
})

const permissionUserTotalPages = computed(() => Math.max(1, Math.ceil(filteredPermissionUsers.value.length / permissionUserPageSize)))
const permissionUserPages = computed(() =>
  Array.from({ length: permissionUserTotalPages.value }, (_, index) => index + 1),
)
const paginatedPermissionUsers = computed(() => {
  if (permissionUserPage.value > permissionUserTotalPages.value) {
    permissionUserPage.value = permissionUserTotalPages.value
  }

  const start = (permissionUserPage.value - 1) * permissionUserPageSize
  return filteredPermissionUsers.value.slice(start, start + permissionUserPageSize)
})

function goToPermissionListPage(page: number): void {
  permissionListPage.value = Math.min(Math.max(page, 1), permissionListTotalPages.value)
}

function goToPermissionRolePage(page: number): void {
  permissionRolePage.value = Math.min(Math.max(page, 1), permissionRoleTotalPages.value)
}

function goToPermissionUserPage(page: number): void {
  permissionUserPage.value = Math.min(Math.max(page, 1), permissionUserTotalPages.value)
}

function updateAssignmentSearchTerm(event: Event): void {
  assignmentSearchTerm.value = (event.target as HTMLInputElement).value
}

function clearPermissionDraft(): void {
  props.permissionForm.codigo = ''
  props.permissionForm.nombre = ''
  props.permissionForm.modulo = ''
  props.permissionForm.accion = ''
  props.permissionForm.descripcion = ''
  props.permissionForm.estado = true
  props.permissionForm.role_ids = []
  props.permissionForm.user_ids = []
}

function applyPermissionToDraft(permission: AccessPermission): void {
  props.permissionForm.codigo = permission.codigo
  props.permissionForm.nombre = permission.nombre
  props.permissionForm.modulo = permission.modulo
  props.permissionForm.accion = permission.accion
  props.permissionForm.descripcion = permission.descripcion
  props.permissionForm.estado = permission.estado
  props.permissionForm.role_ids = [...permission.role_ids]
  props.permissionForm.user_ids = [...permission.user_ids]
}

function toggleSelection(collection: string[], value: string): string[] {
  return collection.includes(value) ? collection.filter((item) => item !== value) : [...collection, value]
}

function hasAllSelected(collection: string[], values: string[]): boolean {
  return values.length > 0 && values.every((value) => collection.includes(value))
}

function toggleBulkSelection(collection: string[], values: string[]): string[] {
  if (values.length === 0) {
    return collection
  }

  if (hasAllSelected(collection, values)) {
    return collection.filter((item) => !values.includes(item))
  }

  return [...new Set([...collection, ...values])]
}

function togglePermissionRole(roleId: string): void {
  props.permissionForm.role_ids = toggleSelection(props.permissionForm.role_ids, roleId)
}

function togglePermissionUser(userId: string): void {
  props.permissionForm.user_ids = toggleSelection(props.permissionForm.user_ids, userId)
}

function toggleVisiblePermissionRoles(): void {
  props.permissionForm.role_ids = toggleBulkSelection(
    props.permissionForm.role_ids,
    paginatedPermissionRoles.value.map((role) => role.id),
  )
}

function toggleVisiblePermissionUsers(): void {
  props.permissionForm.user_ids = toggleBulkSelection(
    props.permissionForm.user_ids,
    paginatedPermissionUsers.value.map((user) => user.id),
  )
}

function handleCreatePermission(): void {
  localSelectedPermissionId.value = null
  emit('create-permission')
  activePermissionTab.value = 'datos'
  assignmentSearchTerm.value = ''
}

function handleSelectPermission(permission: AccessPermission): void {
  if (currentSelectedPermissionId.value === permission.id) {
    handleCreatePermission()
    return
  }

  localSelectedPermissionId.value = permission.id
  applyPermissionToDraft(permission)
  emit('select-permission', permission)
  activePermissionTab.value = 'datos'
  assignmentSearchTerm.value = ''
}

function getUserRoleLabels(user: AccessUser): string[] {
  return user.role_ids
    .map((roleId) => roleLabelById.value.get(roleId))
    .filter((label): label is string => Boolean(label))
}

function getRoleUserCount(role: AccessRole): number {
  return props.sortedUsers.filter((user) => user.role_ids.includes(role.id)).length
}

function selectPermissionTab(tab: PermissionTab): void {
  activePermissionTab.value = tab
  if (tab !== 'datos') {
    assignmentSearchTerm.value = ''
  }
}

watch(filteredPermissionRoles, () => {
  permissionRolePage.value = 1
})

watch(permissionRoleTotalPages, (totalPages) => {
  if (permissionRolePage.value > totalPages) {
    permissionRolePage.value = totalPages
  }
})

watch(filteredPermissionUsers, () => {
  permissionUserPage.value = 1
})

watch(permissionUserTotalPages, (totalPages) => {
  if (permissionUserPage.value > totalPages) {
    permissionUserPage.value = totalPages
  }
})

watch(
  () => props.selectedPermissionId,
  (selectedPermissionId) => {
    localSelectedPermissionId.value = selectedPermissionId
  },
  { immediate: true },
)
</script>

<template>
  <div class="users-role-layout">
    <section class="card card--acrylic tracking-card users-role-list-card" aria-label="Listado de permisos">
      <div class="card__body users-role-list">
        <div class="tracking-field">
          <span class="input-label">Buscar permiso</span>
          <label class="search-input search-input--sm" aria-label="Buscar permiso">
            <span class="search-input__icon" aria-hidden="true">
              <svg viewBox="0 0 16 16" fill="none">
                <path d="M7.25 12.25A5 5 0 1 0 7.25 2.25a5 5 0 0 0 0 10ZM11 11l3 3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
              </svg>
            </span>
            <input
              :value="permissionSearchTerm"
              class="search-input__field"
              type="text"
              placeholder="Codigo, nombre, modulo o accion"
              @input="updatePermissionSearchTerm"
            />
          </label>
        </div>

        <button
          v-for="permission in paginatedPermissions"
          :key="permission.id"
          type="button"
          class="users-role-item"
          :class="{ 'users-role-item--active': currentSelectedPermissionId === permission.id }"
          @click="handleSelectPermission(permission)"
        >
          <span class="users-role-item-header">
            <span class="users-role-item-name">{{ permission.nombre }}</span>
            <span
              class="users-role-item-status"
              :class="permission.estado ? 'users-role-item-status--active' : 'users-role-item-status--inactive'"
            >
              <span class="status-dot" :class="permission.estado ? '' : 'status-dot--offline'" aria-hidden="true" />
              <span>{{ permission.estado ? 'Activo' : 'Inactivo' }}</span>
            </span>
          </span>
          <span class="users-role-item-footer">
            <span class="users-role-item-code">{{ permission.codigo }}</span>
            <span class="badge badge--sm badge--info">{{ permission.modulo || 'General' }}</span>
          </span>
        </button>

        <div class="users-role-list-footer">
          <nav
            v-if="filteredPermissions.length > 0"
            class="pagination pagination--sm users-pagination users-pagination--roles-compact"
            aria-label="Paginacion de permisos"
          >
            <button
              type="button"
              class="pagination__prev"
              aria-label="Previous page"
              :disabled="permissionListPage === 1"
              @click="goToPermissionListPage(permissionListPage - 1)"
            >
              <span aria-hidden="true">‹</span>
            </button>

            <button
              v-for="page in permissionListPages"
              :key="`permission-list-page-${page}`"
              type="button"
              class="pagination__page"
              :aria-current="page === permissionListPage ? 'page' : undefined"
              @click="goToPermissionListPage(page)"
            >
              {{ page }}
            </button>

            <button
              type="button"
              class="pagination__next"
              aria-label="Next page"
              :disabled="permissionListPage === permissionListTotalPages"
              @click="goToPermissionListPage(permissionListPage + 1)"
            >
              <span aria-hidden="true">›</span>
            </button>
          </nav>
        </div>
      </div>
    </section>

    <section
      class="card card--acrylic tracking-card users-role-card"
      :class="{ 'users-role-card--datos': activePermissionTab === 'datos' }"
      aria-label="Formulario de permiso"
    >
      <header class="card__header tracking-card-header--space-between users-role-editor-header">
        <div class="users-role-editor-copy">
          <p class="card__header-title tracking-card-title">
            {{ resolvedPermissionFormMode === 'create' ? 'NUEVO PERMISO' : 'EDITAR PERMISO' }}
            <span class="users-role-editor-inline-copy">: Define el permiso, sus roles y usuarios directos.</span>
          </p>
        </div>

        <div class="users-role-editor-actions">
          <button v-if="resolvedPermissionFormMode === 'edit'" type="button" class="btn btn--primary btn--sm" @click="handleCreatePermission">
            Nuevo permiso
          </button>
          <button type="button" class="btn btn--ghost btn--sm" @click="clearPermissionDraft">
            Limpiar
          </button>
        </div>
      </header>

      <div class="card__body users-role-body">
        <section class="users-access-panel">
          <div class="tabs tabs--pills users-role-tabs" role="tablist" aria-label="Edicion del permiso">
            <button
              type="button"
              class="tab"
              :class="{ 'tab--active': activePermissionTab === 'datos' }"
              role="tab"
              :aria-selected="activePermissionTab === 'datos'"
              @click="selectPermissionTab('datos')"
            >
              Datos
            </button>
            <button
              type="button"
              class="tab"
              :class="{ 'tab--active': activePermissionTab === 'roles' }"
              role="tab"
              :aria-selected="activePermissionTab === 'roles'"
              @click="selectPermissionTab('roles')"
            >
              Roles
            </button>
            <button
              type="button"
              class="tab"
              :class="{ 'tab--active': activePermissionTab === 'usuarios' }"
              role="tab"
              :aria-selected="activePermissionTab === 'usuarios'"
              @click="selectPermissionTab('usuarios')"
            >
              Usuarios
            </button>
          </div>

          <div class="users-role-context-strip">
            <div class="users-role-context-heading">
              <span class="users-review-name">{{ permissionForm.nombre || 'Permiso sin nombre' }}</span>
              <span class="badge" :class="permissionForm.estado ? 'badge--success' : 'badge--danger'">
                {{ permissionForm.estado ? 'Activo' : 'Inactivo' }}
              </span>
            </div>

            <div class="users-role-context-meta">
              <span class="users-role-context-pill">
                <strong>{{ permissionForm.codigo || '-' }}</strong>
              </span>
              <span class="users-role-context-pill">
                <strong>{{ permissionForm.modulo || 'General' }}</strong>
              </span>
              <span class="users-role-context-pill">
                <strong>{{ permissionForm.role_ids.length }}</strong>
                <span>roles</span>
              </span>
              <span class="users-role-context-pill">
                <svg viewBox="0 0 16 16" fill="none" aria-hidden="true">
                  <path
                    d="M8 8.2A2.85 2.85 0 1 0 8 2.5a2.85 2.85 0 0 0 0 5.7Zm0 1.55c-2.56 0-4.64 1.4-4.64 3.12v.63h9.28v-.63c0-1.72-2.08-3.12-4.64-3.12Z"
                    fill="currentColor"
                  />
                </svg>
                <strong>{{ permissionForm.user_ids.length }}</strong>
              </span>
            </div>

            <div v-if="activePermissionTab === 'datos'" class="users-permission-inline-form">
              <label class="tracking-field">
                <span class="input-label">Codigo</span>
                <input
                  v-model="permissionForm.codigo"
                  class="input input--sm"
                  :class="{ 'input--error': permissionValidationAttempted && permissionFormErrors.codigo }"
                  type="text"
                  placeholder="USR_EDIT"
                />
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

              <label class="users-toggle toggle toggle--success">
                <input v-model="permissionForm.estado" class="toggle__input" type="checkbox" />
                <span class="toggle__track" aria-hidden="true">
                  <span class="toggle__thumb" />
                </span>
                <span class="toggle__label">Permiso activo</span>
              </label>
            </div>
          </div>

          <div v-if="activePermissionTab !== 'datos'" class="users-assignment-toolbar">
            <div class="tracking-field users-role-assignment-search">
              <span class="input-label">{{ activePermissionTab === 'roles' ? 'Buscar rol' : 'Buscar usuario' }}</span>
              <label class="search-input search-input--sm" :aria-label="activePermissionTab === 'roles' ? 'Buscar rol' : 'Buscar usuario'">
                <span class="search-input__icon" aria-hidden="true">
                  <svg viewBox="0 0 16 16" fill="none">
                    <path d="M7.25 12.25A5 5 0 1 0 7.25 2.25a5 5 0 0 0 0 10ZM11 11l3 3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
                  </svg>
                </span>
                <input
                  :value="assignmentSearchTerm"
                  class="search-input__field"
                  type="text"
                  :placeholder="activePermissionTab === 'roles' ? 'Rol, codigo o descripcion' : 'Usuario, username o area'"
                  @input="updateAssignmentSearchTerm"
                />
              </label>
            </div>

            <label
              v-if="activePermissionTab === 'roles' && paginatedPermissionRoles.length > 0"
              class="checkbox users-bulk-select users-bulk-select--toolbar"
            >
              <input
                :checked="hasAllSelected(permissionForm.role_ids, paginatedPermissionRoles.map((role) => role.id))"
                class="checkbox__input"
                type="checkbox"
                @change="toggleVisiblePermissionRoles"
              />
              <span class="checkbox__box" aria-hidden="true" />
              <span class="users-bulk-select__label">Seleccionar todo</span>
            </label>

            <label
              v-else-if="activePermissionTab === 'usuarios' && paginatedPermissionUsers.length > 0"
              class="checkbox users-bulk-select users-bulk-select--toolbar"
            >
              <input
                :checked="hasAllSelected(permissionForm.user_ids, paginatedPermissionUsers.map((user) => user.id))"
                class="checkbox__input"
                type="checkbox"
                @change="toggleVisiblePermissionUsers"
              />
              <span class="checkbox__box" aria-hidden="true" />
              <span class="users-bulk-select__label">Seleccionar todo</span>
            </label>
          </div>

          <div v-if="activePermissionTab === 'roles'" class="users-permission-tab-section">
            <div class="users-role-selector-grid">
            <label
              v-for="role in paginatedPermissionRoles"
              :key="role.id"
              class="users-role-choice checkbox"
              :class="{ 'users-role-choice--active': permissionForm.role_ids.includes(role.id) }"
            >
              <input
                :checked="permissionForm.role_ids.includes(role.id)"
                class="checkbox__input"
                type="checkbox"
                @change="togglePermissionRole(role.id)"
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
                <span class="users-role-choice-tags">
                  <span class="badge badge--sm badge--info">{{ getRoleUserCount(role) }} usuarios</span>
                </span>
              </span>
            </label>

            <p v-if="filteredPermissionRoles.length === 0" class="users-empty-state users-selector-empty">
              No hay roles que coincidan con la busqueda.
            </p>
          </div>
            <nav
              v-if="filteredPermissionRoles.length > 0"
              class="pagination pagination--sm users-pagination users-pagination--roles-compact users-tab-pagination"
              aria-label="Paginacion de roles asociados"
            >
              <button
                type="button"
                class="pagination__prev"
                aria-label="Previous page"
                :disabled="permissionRolePage === 1"
                @click="goToPermissionRolePage(permissionRolePage - 1)"
              >
                <span aria-hidden="true">‹</span>
              </button>

              <button
                v-for="page in permissionRolePages"
                :key="`permission-role-page-${page}`"
                type="button"
                class="pagination__page"
                :aria-current="page === permissionRolePage ? 'page' : undefined"
                @click="goToPermissionRolePage(page)"
              >
                {{ page }}
              </button>

              <button
                type="button"
                class="pagination__next"
                aria-label="Next page"
                :disabled="permissionRolePage === permissionRoleTotalPages"
                @click="goToPermissionRolePage(permissionRolePage + 1)"
              >
                <span aria-hidden="true">›</span>
              </button>
            </nav>
          </div>

          <div v-else-if="activePermissionTab === 'usuarios'" class="users-permission-tab-section">
            <div class="users-selector-grid">
            <label
              v-for="user in paginatedPermissionUsers"
              :key="user.id"
              class="users-role-choice checkbox"
              :class="{ 'users-role-choice--active': permissionForm.user_ids.includes(user.id) }"
            >
              <input
                :checked="permissionForm.user_ids.includes(user.id)"
                class="checkbox__input"
                type="checkbox"
                @change="togglePermissionUser(user.id)"
              />
              <span class="checkbox__box" aria-hidden="true" />
              <span class="users-role-choice-copy">
                <span class="users-role-choice-heading">
                  <span class="users-role-choice-name">{{ user.fullname || user.username }}</span>
                  <span class="users-role-choice-status" :class="user.is_active ? 'users-role-choice-status--active' : 'users-role-choice-status--inactive'">
                    <span class="status-dot" :class="user.is_active ? '' : 'status-dot--offline'" aria-hidden="true" />
                    <span>{{ user.is_active ? 'Activo' : 'Inactivo' }}</span>
                  </span>
                </span>
                <span class="users-role-choice-meta">{{ user.username }}</span>
                <span class="users-role-choice-tags">
                  <span v-if="user.area" class="badge badge--sm badge--info">{{ user.area }}</span>
                  <span
                    v-for="roleLabel in getUserRoleLabels(user)"
                    :key="`${user.id}-${roleLabel}`"
                    class="badge badge--sm badge--secondary"
                  >
                    {{ roleLabel }}
                  </span>
                </span>
              </span>
            </label>

            <p v-if="filteredPermissionUsers.length === 0" class="users-empty-state users-selector-empty">
              No hay usuarios que coincidan con la busqueda.
            </p>
          </div>
            <nav
              v-if="filteredPermissionUsers.length > 0"
              class="pagination pagination--sm users-pagination users-pagination--roles-compact users-tab-pagination"
              aria-label="Paginacion de usuarios asociados"
            >
              <button
                type="button"
                class="pagination__prev"
                aria-label="Previous page"
                :disabled="permissionUserPage === 1"
                @click="goToPermissionUserPage(permissionUserPage - 1)"
              >
                <span aria-hidden="true">‹</span>
              </button>

              <button
                v-for="page in permissionUserPages"
                :key="`permission-user-page-${page}`"
                type="button"
                class="pagination__page"
                :aria-current="page === permissionUserPage ? 'page' : undefined"
                @click="goToPermissionUserPage(page)"
              >
                {{ page }}
              </button>

              <button
                type="button"
                class="pagination__next"
                aria-label="Next page"
                :disabled="permissionUserPage === permissionUserTotalPages"
                @click="goToPermissionUserPage(permissionUserPage + 1)"
              >
                <span aria-hidden="true">›</span>
              </button>
            </nav>
          </div>
        </section>

        <div class="users-form-actions" :class="{ 'users-form-actions--end': activePermissionTab === 'datos' }">
          <button type="button" class="btn btn--primary btn--sm users-role-submit-button" :disabled="isSavingPermission" @click="emit('save-permission')">
            {{ isSavingPermission ? 'GUARDANDO...' : resolvedPermissionFormMode === 'create' ? 'CREAR PERMISO' : 'ACTUALIZAR PERMISO' }}
          </button>
        </div>
      </div>
    </section>
  </div>
</template>
