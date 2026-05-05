<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import type { AccessPermission, AccessRole, AccessUser, RolePayload } from '../types'

type PermissionGroup = { moduleName: string; permissions: AccessPermission[] }
type RoleTab = 'datos' | 'usuarios' | 'permisos'

const activeRoleTab = ref<RoleTab>('datos')
const roleListPage = ref(1)
const roleListPageSize = 4
const roleUserPage = ref(1)
const roleUserPageSize = 6
const rolePermissionPage = ref(1)
const rolePermissionPageSize = 9
const assignmentSearchTerm = ref('')
const localSelectedRoleId = ref<string | null>(null)

const props = defineProps<{
  roleSearchTerm: string
  filteredRoles: AccessRole[]
  selectedRoleId: string | null
  roleFormMode: 'create' | 'edit'
  roleForm: RolePayload
  sortedUsers: AccessUser[]
  roleOptions: AccessRole[]
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
  roleListPage.value = 1
}

const roleListTotalPages = computed(() => Math.max(1, Math.ceil(props.filteredRoles.length / roleListPageSize)))

const roleListPages = computed(() =>
  Array.from({ length: roleListTotalPages.value }, (_, index) => index + 1),
)

const paginatedRoles = computed(() => {
  if (roleListPage.value > roleListTotalPages.value) {
    roleListPage.value = roleListTotalPages.value
  }

  const start = (roleListPage.value - 1) * roleListPageSize
  return props.filteredRoles.slice(start, start + roleListPageSize)
})

const currentSelectedRoleId = computed(() => props.selectedRoleId ?? localSelectedRoleId.value)
const resolvedRoleFormMode = computed<'create' | 'edit'>(() =>
  currentSelectedRoleId.value ? 'edit' : props.roleFormMode,
)

const normalizedAssignmentSearch = computed(() => assignmentSearchTerm.value.trim().toLowerCase())

const roleLabelById = computed(() => {
  const labels = new Map<string, string>()
  props.roleOptions.forEach((role) => {
    labels.set(role.id, role.nombre || role.codigo)
  })
  return labels
})

const filteredRoleUsers = computed(() => {
  const search = normalizedAssignmentSearch.value

  if (!search) {
    return props.sortedUsers
  }

  return props.sortedUsers.filter((user) => {
    const roleLabels = getUserRoleLabels(user).join(' ')
    const criteria = [user.fullname, user.username, user.area, roleLabels]
    return criteria.some((value) => value.toLowerCase().includes(search))
  })
})

const filteredRolePermissions = computed(() => {
  const permissions = props.permissionsByModule.flatMap((group) => group.permissions)
  const search = normalizedAssignmentSearch.value

  if (!search) {
    return permissions
  }

  return permissions.filter((permission) => {
    const criteria = [permission.nombre, permission.codigo, permission.modulo, permission.accion, permission.descripcion]
    return criteria.some((value) => value.toLowerCase().includes(search))
  })
})

const roleUserTotalPages = computed(() => Math.max(1, Math.ceil(filteredRoleUsers.value.length / roleUserPageSize)))
const roleUserPages = computed(() =>
  Array.from({ length: roleUserTotalPages.value }, (_, index) => index + 1),
)
const paginatedRoleUsers = computed(() => {
  if (roleUserPage.value > roleUserTotalPages.value) {
    roleUserPage.value = roleUserTotalPages.value
  }

  const start = (roleUserPage.value - 1) * roleUserPageSize
  return filteredRoleUsers.value.slice(start, start + roleUserPageSize)
})

const rolePermissionTotalPages = computed(() => Math.max(1, Math.ceil(filteredRolePermissions.value.length / rolePermissionPageSize)))
const rolePermissionPages = computed(() =>
  Array.from({ length: rolePermissionTotalPages.value }, (_, index) => index + 1),
)
const paginatedRolePermissions = computed(() => {
  if (rolePermissionPage.value > rolePermissionTotalPages.value) {
    rolePermissionPage.value = rolePermissionTotalPages.value
  }

  const start = (rolePermissionPage.value - 1) * rolePermissionPageSize
  return filteredRolePermissions.value.slice(start, start + rolePermissionPageSize)
})

function getUserRoleLabels(user: AccessUser): string[] {
  return user.role_ids
    .map((roleId) => roleLabelById.value.get(roleId))
    .filter((label): label is string => Boolean(label))
}

function getRoleUserCount(role: AccessRole): number {
  return props.sortedUsers.filter((user) => user.role_ids.includes(role.id)).length
}

function goToRoleListPage(page: number): void {
  roleListPage.value = Math.min(Math.max(page, 1), roleListTotalPages.value)
}

function goToRoleUserPage(page: number): void {
  roleUserPage.value = Math.min(Math.max(page, 1), roleUserTotalPages.value)
}

function goToRolePermissionPage(page: number): void {
  rolePermissionPage.value = Math.min(Math.max(page, 1), rolePermissionTotalPages.value)
}

function updateAssignmentSearchTerm(event: Event): void {
  assignmentSearchTerm.value = (event.target as HTMLInputElement).value
}

function clearRoleDraft(): void {
  props.roleForm.codigo = ''
  props.roleForm.nombre = ''
  props.roleForm.descripcion = ''
  props.roleForm.estado = true
  props.roleForm.permission_ids = []
  props.roleForm.user_ids = []
}

function applyRoleToDraft(role: AccessRole): void {
  props.roleForm.codigo = role.codigo
  props.roleForm.nombre = role.nombre
  props.roleForm.descripcion = role.descripcion
  props.roleForm.estado = role.estado
  props.roleForm.permission_ids = [...role.permission_ids]
  props.roleForm.user_ids = [...role.user_ids]
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

function toggleRolePermission(permissionId: string): void {
  props.roleForm.permission_ids = toggleSelection(props.roleForm.permission_ids, permissionId)
}

function toggleRoleUser(userId: string): void {
  props.roleForm.user_ids = toggleSelection(props.roleForm.user_ids, userId)
}

function toggleVisibleRoleUsers(): void {
  props.roleForm.user_ids = toggleBulkSelection(
    props.roleForm.user_ids,
    paginatedRoleUsers.value.map((user) => user.id),
  )
}

function toggleVisibleRolePermissions(): void {
  props.roleForm.permission_ids = toggleBulkSelection(
    props.roleForm.permission_ids,
    paginatedRolePermissions.value.map((permission) => permission.id),
  )
}

function handleCreateRole(): void {
  localSelectedRoleId.value = null
  emit('create-role')
  activeRoleTab.value = 'datos'
  assignmentSearchTerm.value = ''
}

function handleSelectRole(role: AccessRole): void {
  if (currentSelectedRoleId.value === role.id) {
    handleCreateRole()
    return
  }

  localSelectedRoleId.value = role.id
  applyRoleToDraft(role)
  emit('select-role', role)
  activeRoleTab.value = 'datos'
  assignmentSearchTerm.value = ''
}

function selectRoleTab(tab: RoleTab): void {
  activeRoleTab.value = tab
  if (tab !== 'datos') {
    assignmentSearchTerm.value = ''
  }
}

watch(filteredRoleUsers, () => {
  roleUserPage.value = 1
})

watch(roleUserTotalPages, (totalPages) => {
  if (roleUserPage.value > totalPages) {
    roleUserPage.value = totalPages
  }
})

watch(filteredRolePermissions, () => {
  rolePermissionPage.value = 1
})

watch(rolePermissionTotalPages, (totalPages) => {
  if (rolePermissionPage.value > totalPages) {
    rolePermissionPage.value = totalPages
  }
})

watch(
  () => props.selectedRoleId,
  (selectedRoleId) => {
    localSelectedRoleId.value = selectedRoleId
  },
  { immediate: true },
)
</script>

<template>
  <div class="users-role-layout">
    <section class="card card--acrylic tracking-card users-role-list-card" aria-label="Listado de roles">
      <div class="card__body users-role-list">
        <div class="tracking-field">
          <span class="input-label">Buscar rol</span>
          <label class="search-input search-input--sm" aria-label="Buscar rol">
            <span class="search-input__icon" aria-hidden="true">
              <svg viewBox="0 0 16 16" fill="none">
                <path d="M7.25 12.25A5 5 0 1 0 7.25 2.25a5 5 0 0 0 0 10ZM11 11l3 3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
              </svg>
            </span>
            <input
              :value="roleSearchTerm"
              class="search-input__field"
              type="text"
              placeholder="Codigo, nombre o descripcion"
              @input="updateRoleSearchTerm"
            />
          </label>
        </div>

        <button
          v-for="role in paginatedRoles"
          :key="role.id"
          type="button"
          class="users-role-item"
          :class="{ 'users-role-item--active': currentSelectedRoleId === role.id }"
          @click="handleSelectRole(role)"
        >
          <span class="users-role-item-header">
            <span class="users-role-item-name">{{ role.nombre }}</span>
            <span
              class="users-role-item-status"
              :class="role.estado ? 'users-role-item-status--active' : 'users-role-item-status--inactive'"
            >
              <span class="status-dot" :class="role.estado ? '' : 'status-dot--offline'" aria-hidden="true" />
              <span>{{ role.estado ? 'Activo' : 'Inactivo' }}</span>
            </span>
          </span>
          <span class="users-role-item-footer">
            <span class="users-role-item-code">{{ role.codigo }}</span>
            <span class="badge badge--sm badge--info users-role-user-count">
              <svg viewBox="0 0 16 16" fill="none" aria-hidden="true">
                <path
                  d="M8 8.2A2.85 2.85 0 1 0 8 2.5a2.85 2.85 0 0 0 0 5.7Zm0 1.55c-2.56 0-4.64 1.4-4.64 3.12v.63h9.28v-.63c0-1.72-2.08-3.12-4.64-3.12Z"
                  fill="currentColor"
                />
              </svg>
              <span>{{ getRoleUserCount(role) }}</span>
            </span>
          </span>
        </button>

        <div class="users-role-list-footer">
          <nav v-if="filteredRoles.length > 0" class="pagination pagination--sm users-pagination users-pagination--roles-compact" aria-label="Paginacion de roles">
            <button
              type="button"
              class="pagination__prev"
              aria-label="Previous page"
              :disabled="roleListPage === 1"
              @click="goToRoleListPage(roleListPage - 1)"
            >
              <span aria-hidden="true">‹</span>
            </button>

            <button
              v-for="page in roleListPages"
              :key="`role-list-page-${page}`"
              type="button"
              class="pagination__page"
              :aria-current="page === roleListPage ? 'page' : undefined"
              @click="goToRoleListPage(page)"
            >
              {{ page }}
            </button>

            <button
              type="button"
              class="pagination__next"
              aria-label="Next page"
              :disabled="roleListPage === roleListTotalPages"
              @click="goToRoleListPage(roleListPage + 1)"
            >
              <span aria-hidden="true">›</span>
            </button>
          </nav>
        </div>
      </div>
    </section>

    <section
      class="card card--acrylic tracking-card users-role-card"
      :class="{ 'users-role-card--datos': activeRoleTab === 'datos' }"
      aria-label="Formulario de rol"
    >
      <header class="card__header tracking-card-header--space-between users-role-editor-header">
        <div class="users-role-editor-copy">
          <p class="card__header-title tracking-card-title">
            {{ resolvedRoleFormMode === 'create' ? 'NUEVO ROL' : 'EDITAR ROL' }}
            <span class="users-role-editor-inline-copy">: Define el rol, sus permisos y los usuarios que lo heredan.</span>
          </p>
        </div>

        <div class="users-role-editor-actions">
          <button v-if="resolvedRoleFormMode === 'edit'" type="button" class="btn btn--primary btn--sm" @click="handleCreateRole">
            Nuevo rol
          </button>
          <button type="button" class="btn btn--ghost btn--sm" @click="clearRoleDraft">
            Limpiar
          </button>
        </div>
      </header>

      <div class="card__body users-role-body">
        <section class="users-access-panel">
          <div class="tabs tabs--pills users-role-tabs" role="tablist" aria-label="Edicion del rol">
            <button
              type="button"
              class="tab"
              :class="{ 'tab--active': activeRoleTab === 'datos' }"
              role="tab"
              :aria-selected="activeRoleTab === 'datos'"
              @click="selectRoleTab('datos')"
            >
              Datos
            </button>
            <button
              type="button"
              class="tab"
              :class="{ 'tab--active': activeRoleTab === 'usuarios' }"
              role="tab"
              :aria-selected="activeRoleTab === 'usuarios'"
              @click="selectRoleTab('usuarios')"
            >
              Usuarios
            </button>
            <button
              type="button"
              class="tab"
              :class="{ 'tab--active': activeRoleTab === 'permisos' }"
              role="tab"
              :aria-selected="activeRoleTab === 'permisos'"
              @click="selectRoleTab('permisos')"
            >
              Permisos base
            </button>
          </div>

          <div class="users-role-context-strip">
            <div class="users-role-context-heading">
              <span class="users-review-name">{{ roleForm.nombre || 'Rol sin nombre' }}</span>
              <span class="badge" :class="roleForm.estado ? 'badge--success' : 'badge--danger'">
                {{ roleForm.estado ? 'Activo' : 'Inactivo' }}
              </span>
            </div>

            <div class="users-role-context-meta">
              <span class="users-role-context-pill">
                <strong>{{ roleForm.codigo || '-' }}</strong>
              </span>
              <span class="users-role-context-pill">
                <svg viewBox="0 0 16 16" fill="none" aria-hidden="true">
                  <path
                    d="M8 8.2A2.85 2.85 0 1 0 8 2.5a2.85 2.85 0 0 0 0 5.7Zm0 1.55c-2.56 0-4.64 1.4-4.64 3.12v.63h9.28v-.63c0-1.72-2.08-3.12-4.64-3.12Z"
                    fill="currentColor"
                  />
                </svg>
                <strong>{{ roleForm.user_ids.length }}</strong>
              </span>
              <span class="users-role-context-pill">
                <strong>{{ roleForm.permission_ids.length }}</strong>
                <span>permisos</span>
              </span>
            </div>

            <div v-if="activeRoleTab === 'datos'" class="users-role-inline-form">
              <label class="tracking-field">
                <span class="input-label">Codigo</span>
                <input
                  v-model="roleForm.codigo"
                  class="input input--sm"
                  :class="{ 'input--error': roleValidationAttempted && roleFormErrors.codigo }"
                  type="text"
                  placeholder="ADMIN"
                />
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
              </label>

              <label class="tracking-field users-field-span-2">
                <span class="input-label">Descripcion</span>
                <input v-model="roleForm.descripcion" class="input input--sm" type="text" placeholder="Rol con acceso amplio al modulo" />
              </label>

              <label class="users-toggle toggle toggle--success">
                <input v-model="roleForm.estado" class="toggle__input" type="checkbox" />
                <span class="toggle__track" aria-hidden="true">
                  <span class="toggle__thumb" />
                </span>
                <span class="toggle__label">Rol activo</span>
              </label>
            </div>
          </div>

          <div v-if="activeRoleTab === 'usuarios'" class="users-permission-tab-section">
            <div class="users-assignment-toolbar">
              <div class="tracking-field users-role-assignment-search">
                <span class="input-label">Buscar usuario</span>
                <label class="search-input search-input--sm" aria-label="Buscar usuario">
                  <span class="search-input__icon" aria-hidden="true">
                    <svg viewBox="0 0 16 16" fill="none">
                      <path d="M7.25 12.25A5 5 0 1 0 7.25 2.25a5 5 0 0 0 0 10ZM11 11l3 3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
                    </svg>
                  </span>
                  <input
                    :value="assignmentSearchTerm"
                    class="search-input__field"
                    type="text"
                    placeholder="Usuario, username, area o rol"
                    @input="updateAssignmentSearchTerm"
                  />
                </label>
              </div>

              <label
                v-if="paginatedRoleUsers.length > 0"
                class="checkbox users-bulk-select users-bulk-select--toolbar"
              >
                <input
                  :checked="hasAllSelected(roleForm.user_ids, paginatedRoleUsers.map((user) => user.id))"
                  class="checkbox__input"
                  type="checkbox"
                  @change="toggleVisibleRoleUsers"
                />
                <span class="checkbox__box" aria-hidden="true" />
                <span class="users-bulk-select__label">Seleccionar todo</span>
              </label>
            </div>

            <div class="users-selector-grid">
            <label
              v-for="user in paginatedRoleUsers"
              :key="user.id"
              class="users-role-choice checkbox"
              :class="{ 'users-role-choice--active': roleForm.user_ids.includes(user.id) }"
            >
              <input
                :checked="roleForm.user_ids.includes(user.id)"
                class="checkbox__input"
                type="checkbox"
                @change="toggleRoleUser(user.id)"
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

            <p v-if="filteredRoleUsers.length === 0" class="users-empty-state users-selector-empty">
              No hay usuarios que coincidan con la busqueda.
            </p>
          </div>
            <nav
              v-if="filteredRoleUsers.length > 0"
              class="pagination pagination--sm users-pagination users-pagination--roles-compact users-tab-pagination"
              aria-label="Paginacion de usuarios del rol"
            >
              <button
                type="button"
                class="pagination__prev"
                aria-label="Previous page"
                :disabled="roleUserPage === 1"
                @click="goToRoleUserPage(roleUserPage - 1)"
              >
                <span aria-hidden="true">‹</span>
              </button>

              <button
                v-for="page in roleUserPages"
                :key="`role-user-page-${page}`"
                type="button"
                class="pagination__page"
                :aria-current="page === roleUserPage ? 'page' : undefined"
                @click="goToRoleUserPage(page)"
              >
                {{ page }}
              </button>

              <button
                type="button"
                class="pagination__next"
                aria-label="Next page"
                :disabled="roleUserPage === roleUserTotalPages"
                @click="goToRoleUserPage(roleUserPage + 1)"
              >
                <span aria-hidden="true">›</span>
              </button>
            </nav>
          </div>

          <div v-else-if="activeRoleTab === 'permisos'" class="users-permission-tab-section">
            <div class="users-assignment-toolbar">
              <div class="tracking-field users-role-assignment-search">
                <span class="input-label">Buscar permiso</span>
                <label class="search-input search-input--sm" aria-label="Buscar permiso">
                  <span class="search-input__icon" aria-hidden="true">
                    <svg viewBox="0 0 16 16" fill="none">
                      <path d="M7.25 12.25A5 5 0 1 0 7.25 2.25a5 5 0 0 0 0 10ZM11 11l3 3" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
                    </svg>
                  </span>
                  <input
                    :value="assignmentSearchTerm"
                    class="search-input__field"
                    type="text"
                    placeholder="Permiso, codigo o modulo"
                    @input="updateAssignmentSearchTerm"
                  />
                </label>
              </div>

              <label
                v-if="paginatedRolePermissions.length > 0"
                class="checkbox users-bulk-select users-bulk-select--toolbar"
              >
                <input
                  :checked="hasAllSelected(roleForm.permission_ids, paginatedRolePermissions.map((permission) => permission.id))"
                  class="checkbox__input"
                  type="checkbox"
                  @change="toggleVisibleRolePermissions"
                />
                <span class="checkbox__box" aria-hidden="true" />
                <span class="users-bulk-select__label">Seleccionar todo</span>
              </label>
            </div>

            <p v-if="filteredRolePermissions.length === 0" class="users-empty-state">
              No hay permisos que coincidan con la busqueda.
            </p>

            <div class="users-role-selector-grid">
              <label
                v-for="permission in paginatedRolePermissions"
                :key="permission.id"
                class="users-permission-choice checkbox"
                :class="{ 'users-permission-choice--active': roleForm.permission_ids.includes(permission.id) }"
              >
                <input
                  :checked="roleForm.permission_ids.includes(permission.id)"
                  class="checkbox__input"
                  type="checkbox"
                  @change="toggleRolePermission(permission.id)"
                />
                <span class="checkbox__box" aria-hidden="true" />
                <span class="users-permission-choice-copy">
                  <span class="users-permission-choice-heading">
                    <span class="users-permission-choice-title-row">
                      <span class="users-permission-choice-name">{{ permission.nombre }}</span>
                      <span class="users-chip-meta">{{ permission.codigo }}</span>
                    </span>
                    <span
                      class="users-role-choice-status"
                      :class="permission.estado ? 'users-role-choice-status--active' : 'users-role-choice-status--inactive'"
                    >
                      <span class="status-dot" :class="permission.estado ? '' : 'status-dot--offline'" aria-hidden="true" />
                      <span>{{ permission.estado ? 'Activo' : 'Inactivo' }}</span>
                    </span>
                  </span>
                  <span v-if="permission.descripcion" class="users-role-choice-description">{{ permission.descripcion }}</span>
                  <span class="users-role-choice-tags">
                    <span v-if="permission.modulo" class="badge badge--sm badge--info">{{ permission.modulo }}</span>
                    <span v-if="permission.accion" class="badge badge--sm badge--secondary">{{ permission.accion }}</span>
                  </span>
                </span>
              </label>
            </div>
            <nav
              v-if="filteredRolePermissions.length > 0"
              class="pagination pagination--sm users-pagination users-pagination--roles-compact users-tab-pagination"
              aria-label="Paginacion de permisos del rol"
            >
              <button
                type="button"
                class="pagination__prev"
                aria-label="Previous page"
                :disabled="rolePermissionPage === 1"
                @click="goToRolePermissionPage(rolePermissionPage - 1)"
              >
                <span aria-hidden="true">‹</span>
              </button>

              <button
                v-for="page in rolePermissionPages"
                :key="`role-permission-page-${page}`"
                type="button"
                class="pagination__page"
                :aria-current="page === rolePermissionPage ? 'page' : undefined"
                @click="goToRolePermissionPage(page)"
              >
                {{ page }}
              </button>

              <button
                type="button"
                class="pagination__next"
                aria-label="Next page"
                :disabled="rolePermissionPage === rolePermissionTotalPages"
                @click="goToRolePermissionPage(rolePermissionPage + 1)"
              >
                <span aria-hidden="true">›</span>
              </button>
            </nav>
          </div>
        </section>

        <div class="users-form-actions" :class="{ 'users-form-actions--end': activeRoleTab === 'datos' }">
          <button type="button" class="btn btn--primary btn--sm users-role-submit-button" :disabled="isSavingRole" @click="emit('save-role')">
            {{ isSavingRole ? 'GUARDANDO...' : resolvedRoleFormMode === 'create' ? 'CREAR ROL' : 'ACTUALIZAR ROL' }}
          </button>
        </div>
      </div>
    </section>
  </div>
</template>
