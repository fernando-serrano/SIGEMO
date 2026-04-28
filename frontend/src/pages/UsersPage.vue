<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'

import AppSidebar from '@/features/navigation/components/AppSidebar.vue'
import {
  createUser,
  fetchAccessCatalog,
  updateRolePermissions,
  updateUser,
  updateUserStatus,
} from '@/features/users/api/users.api'
import type { AccessPermission, AccessRole, AccessUser, UserPayload } from '@/features/users/types'
import AppShell from '@/shared/layouts/AppShell.vue'

const mobileBreakpoint = window.matchMedia('(max-width: 1080px)')

const isSidebarOpen = ref(false)
const isLoading = ref(true)
const loadError = ref('')
const userFeedback = ref('')
const roleFeedback = ref('')
const searchTerm = ref('')
const permissionSearchTerm = ref('')
const selectedUserId = ref<string | null>(null)
const selectedRoleId = ref<string | null>(null)
const formMode = ref<'create' | 'edit'>('create')
const activeSection = ref<'usuarios' | 'roles' | 'permisos'>('usuarios')
const isSavingUser = ref(false)
const isSavingRole = ref(false)

const catalog = reactive<{
  users: AccessUser[]
  roles: AccessRole[]
  permissions: AccessPermission[]
}>({
  users: [],
  roles: [],
  permissions: [],
})

const form = reactive<UserPayload>({
  username: '',
  password_hash: '',
  name: '',
  last_name: '',
  email: '',
  area: '',
  is_active: true,
  role_ids: [],
  permission_ids: [],
})

const rolePermissionDraft = ref<string[]>([])

const summary = computed(() => ({
  users: catalog.users.length,
  activeUsers: catalog.users.filter((user) => user.is_active).length,
  roles: catalog.roles.length,
  permissions: catalog.permissions.length,
}))

const filteredUsers = computed(() => {
  const query = searchTerm.value.trim().toLowerCase()

  if (!query) {
    return catalog.users
  }

  return catalog.users.filter((user) =>
    [user.username, user.fullname, user.email, user.area].some((value) => value.toLowerCase().includes(query)),
  )
})

const selectedRole = computed(() => catalog.roles.find((role) => role.id === selectedRoleId.value) ?? null)

const filteredRoles = computed(() => [...catalog.roles].sort((left, right) => left.nombre.localeCompare(right.nombre)))

const permissionsByModule = computed(() => {
  const grouped = new Map<string, AccessPermission[]>()

  for (const permission of catalog.permissions) {
    const moduleName = permission.modulo || 'general'
    const bucket = grouped.get(moduleName) ?? []
    bucket.push(permission)
    grouped.set(moduleName, bucket)
  }

  return [...grouped.entries()]
    .map(([moduleName, permissions]) => ({
      moduleName,
      permissions,
    }))
    .sort((left, right) => left.moduleName.localeCompare(right.moduleName))
})

const filteredPermissionsByModule = computed(() => {
  const query = permissionSearchTerm.value.trim().toLowerCase()

  if (!query) {
    return permissionsByModule.value
  }

  return permissionsByModule.value
    .map((group) => ({
      moduleName: group.moduleName,
      permissions: group.permissions.filter((permission) =>
        [permission.codigo, permission.nombre, permission.accion, permission.descripcion]
          .join(' ')
          .toLowerCase()
          .includes(query),
      ),
    }))
    .filter((group) => group.permissions.length > 0)
})

function describeUserRoles(user: AccessUser): string {
  const labels = user.role_ids
    .map((roleId) => catalog.roles.find((role) => role.id === roleId)?.nombre ?? '')
    .filter(Boolean)

  return labels.length > 0 ? labels.join(', ') : 'Sin roles'
}

function describeEffectivePermissionCount(user: AccessUser): string {
  return `${user.effective_permission_ids.length} permiso${user.effective_permission_ids.length === 1 ? '' : 's'}`
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

function resetForm(): void {
  form.username = ''
  form.password_hash = ''
  form.name = ''
  form.last_name = ''
  form.email = ''
  form.area = ''
  form.is_active = true
  form.role_ids = []
  form.permission_ids = []
}

function syncFormWithUser(user: AccessUser): void {
  form.username = user.username
  form.password_hash = ''
  form.name = user.name
  form.last_name = user.last_name
  form.email = user.email
  form.area = user.area
  form.is_active = user.is_active
  form.role_ids = [...user.role_ids]
  form.permission_ids = [...user.permission_ids]
}

function selectUser(user: AccessUser): void {
  selectedUserId.value = user.id
  formMode.value = 'edit'
  userFeedback.value = ''
  syncFormWithUser(user)
}

function selectRole(roleId: string): void {
  selectedRoleId.value = roleId
  roleFeedback.value = ''
}

function startCreateUser(): void {
  selectedUserId.value = null
  formMode.value = 'create'
  userFeedback.value = ''
  resetForm()
}

function toggleSelection(collection: string[], value: string): string[] {
  return collection.includes(value) ? collection.filter((item) => item !== value) : [...collection, value]
}

function toggleFormRole(roleId: string): void {
  form.role_ids = toggleSelection(form.role_ids, roleId)
}

function toggleFormPermission(permissionId: string): void {
  form.permission_ids = toggleSelection(form.permission_ids, permissionId)
}

function toggleRoleDraftPermission(permissionId: string): void {
  rolePermissionDraft.value = toggleSelection(rolePermissionDraft.value, permissionId)
}

async function loadModuleData(): Promise<void> {
  isLoading.value = true
  loadError.value = ''

  try {
    const response = await fetchAccessCatalog()
    catalog.users = response.users
    catalog.roles = response.roles
    catalog.permissions = response.permissions

    if (!selectedRoleId.value && response.roles.length > 0) {
      selectedRoleId.value = response.roles[0]?.id ?? null
    }

    if (selectedUserId.value) {
      const refreshedUser = response.users.find((user) => user.id === selectedUserId.value)
      if (refreshedUser) {
        syncFormWithUser(refreshedUser)
      } else {
        startCreateUser()
      }
    }
  } catch (error) {
    loadError.value = error instanceof Error ? error.message : 'No se pudo cargar el modulo de usuarios'
  } finally {
    isLoading.value = false
  }
}

async function saveUser(): Promise<void> {
  isSavingUser.value = true
  userFeedback.value = ''

  try {
    const payload: UserPayload = {
      username: form.username.trim(),
      password_hash: form.password_hash?.trim() || undefined,
      name: form.name.trim(),
      last_name: form.last_name.trim(),
      email: form.email.trim(),
      area: form.area.trim(),
      is_active: form.is_active,
      role_ids: [...form.role_ids],
      permission_ids: [...form.permission_ids],
    }

    const result =
      formMode.value === 'create'
        ? await createUser(payload)
        : await updateUser(selectedUserId.value ?? '', payload)

    userFeedback.value = result.message
    await loadModuleData()

    if (result.user) {
      selectedUserId.value = result.user.id
      formMode.value = 'edit'
      syncFormWithUser(result.user)
    }
  } catch (error) {
    userFeedback.value = error instanceof Error ? error.message : 'No se pudo guardar el usuario'
  } finally {
    isSavingUser.value = false
  }
}

async function toggleUserActive(user: AccessUser): Promise<void> {
  userFeedback.value = ''

  try {
    const result = await updateUserStatus(user.id, !user.is_active)
    userFeedback.value = result.message
    await loadModuleData()

    if (selectedUserId.value === user.id && result.user) {
      syncFormWithUser(result.user)
    }
  } catch (error) {
    userFeedback.value = error instanceof Error ? error.message : 'No se pudo actualizar el estado'
  }
}

async function saveRolePermissionMatrix(): Promise<void> {
  if (!selectedRoleId.value) {
    return
  }

  isSavingRole.value = true
  roleFeedback.value = ''

  try {
    const result = await updateRolePermissions(selectedRoleId.value, {
      permission_ids: rolePermissionDraft.value,
    })

    roleFeedback.value = result.message
    await loadModuleData()
  } catch (error) {
    roleFeedback.value = error instanceof Error ? error.message : 'No se pudieron guardar los permisos del rol'
  } finally {
    isSavingRole.value = false
  }
}

watch(
  selectedRole,
  (role) => {
    rolePermissionDraft.value = role ? [...role.permission_ids] : []
  },
  { immediate: true },
)

onMounted(() => {
  if (mobileBreakpoint.matches) {
    closeSidebar()
  }

  mobileBreakpoint.addEventListener('change', handleViewportChange)
  void loadModuleData()
  startCreateUser()
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

    <section class="users-page" aria-label="Gestion de usuarios y accesos">
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

      <header class="card card--acrylic tracking-card users-hero-card">
        <div class="card__body users-hero">
          <div class="users-hero-copy">
            <p class="eyebrow glow-text--strong">SEGURIDAD Y ACCESOS</p>
            <h1 class="tracking-title">
              GESTION DE USUARIOS
              <span class="tracking-title-accent" />
            </h1>
            <p class="users-hero-text">
              Administra usuarios, asigna roles, define permisos por rol y aplica excepciones puntuales por usuario.
            </p>
          </div>
        </div>
      </header>

      <nav class="card card--acrylic tracking-card users-subnav-card" aria-label="Submodulos de seguridad">
        <div class="card__body users-subnav">
          <button
            type="button"
            class="users-subnav-item"
            :class="{ 'users-subnav-item--active': activeSection === 'usuarios' }"
            @click="activeSection = 'usuarios'"
          >
            Usuarios
          </button>
          <button
            type="button"
            class="users-subnav-item"
            :class="{ 'users-subnav-item--active': activeSection === 'roles' }"
            @click="activeSection = 'roles'"
          >
            Roles
          </button>
          <button
            type="button"
            class="users-subnav-item"
            :class="{ 'users-subnav-item--active': activeSection === 'permisos' }"
            @click="activeSection = 'permisos'"
          >
            Permisos
          </button>
        </div>
      </nav>

      <section v-if="loadError" class="card card--acrylic tracking-card">
        <div class="card__body">
          <p class="users-feedback users-feedback--error">{{ loadError }}</p>
        </div>
      </section>

      <section v-if="isLoading" class="card card--acrylic tracking-card">
        <div class="card__body">
          <p class="users-feedback">Cargando usuarios, roles y permisos...</p>
        </div>
      </section>

      <template v-else-if="activeSection === 'usuarios'">
        <div class="users-summary-grid">
          <article class="card card--acrylic tracking-card users-summary-card">
            <div class="card__body">
              <p class="users-summary-value">{{ summary.users }}</p>
              <p class="users-summary-label">Usuarios registrados</p>
            </div>
          </article>

          <article class="card card--acrylic tracking-card users-summary-card">
            <div class="card__body">
              <p class="users-summary-value">{{ summary.activeUsers }}</p>
              <p class="users-summary-label">Usuarios activos</p>
            </div>
          </article>

          <article class="card card--acrylic tracking-card users-summary-card">
            <div class="card__body">
              <p class="users-summary-value">{{ summary.roles }}</p>
              <p class="users-summary-label">Roles configurados</p>
            </div>
          </article>

          <article class="card card--acrylic tracking-card users-summary-card">
            <div class="card__body">
              <p class="users-summary-value">{{ summary.permissions }}</p>
              <p class="users-summary-label">Permisos disponibles</p>
            </div>
          </article>
        </div>

        <div class="users-management-grid">
          <section class="card card--acrylic tracking-card users-table-card" aria-label="Listado de usuarios">
            <header class="card__header tracking-card-header--space-between">
              <div>
                <p class="card__header-title tracking-card-title">USUARIOS</p>
                <p class="users-card-copy">Consulta, activa o edita accesos individuales.</p>
              </div>

              <button type="button" class="btn btn--primary btn--sm" @click="startCreateUser">
                Nuevo usuario
              </button>
            </header>

            <div class="card__body users-table-body">
              <label class="tracking-field">
                <span class="input-label">Buscar usuario</span>
                <input v-model="searchTerm" class="input input--sm" type="text" placeholder="Usuario, nombre, correo o area" />
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
                      <th>Acciones</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr
                      v-for="user in filteredUsers"
                      :key="user.id"
                      :class="{ 'users-table-row--selected': selectedUserId === user.id }"
                      @click="selectUser(user)"
                    >
                      <td>{{ user.username }}</td>
                      <td>{{ user.fullname || '-' }}</td>
                      <td>{{ user.email || '-' }}</td>
                      <td>{{ user.area || '-' }}</td>
                      <td>{{ describeUserRoles(user) }}</td>
                      <td>{{ describeEffectivePermissionCount(user) }}</td>
                      <td>
                        <span class="badge badge--sm" :class="user.is_active ? 'badge--success' : 'badge--danger'">
                          {{ user.is_active ? 'Activo' : 'Inactivo' }}
                        </span>
                      </td>
                      <td class="users-table-actions">
                        <button type="button" class="btn btn--ghost btn--sm" @click.stop="selectUser(user)">Editar</button>
                        <button type="button" class="btn btn--ghost btn--sm" @click.stop="toggleUserActive(user)">
                          {{ user.is_active ? 'Desactivar' : 'Activar' }}
                        </button>
                      </td>
                    </tr>
                    <tr v-if="filteredUsers.length === 0">
                      <td colspan="8" class="tracking-empty">No hay usuarios que coincidan con la busqueda.</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </section>

          <section class="card card--acrylic tracking-card users-form-card" aria-label="Formulario de usuario">
            <header class="card__header tracking-card-header--space-between">
              <div>
                <p class="card__header-title tracking-card-title">
                  {{ formMode === 'create' ? 'NUEVO USUARIO' : 'EDITAR USUARIO' }}
                </p>
                <p class="users-card-copy">Asigna roles, permisos directos y estado operativo.</p>
              </div>

              <button type="button" class="btn btn--ghost btn--sm" @click="startCreateUser">
                Limpiar
              </button>
            </header>

            <div class="card__body users-form-body">
              <div class="users-form-grid">
                <label class="tracking-field">
                  <span class="input-label">Username</span>
                  <input v-model="form.username" class="input input--sm" type="text" placeholder="usuario.sigemo" />
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
                  <span class="input-label">Nombres</span>
                  <input v-model="form.name" class="input input--sm" type="text" placeholder="Fernando Jesus" />
                </label>

                <label class="tracking-field">
                  <span class="input-label">Apellidos</span>
                  <input v-model="form.last_name" class="input input--sm" type="text" placeholder="Serrano Garrido" />
                </label>

                <label class="tracking-field">
                  <span class="input-label">Correo</span>
                  <input v-model="form.email" class="input input--sm" type="email" placeholder="correo@liderman.com.pe" />
                </label>

                <label class="tracking-field">
                  <span class="input-label">Area</span>
                  <input v-model="form.area" class="input input--sm" type="text" placeholder="Operaciones, RRHH, SSO..." />
                </label>
              </div>

              <label class="users-toggle">
                <input v-model="form.is_active" type="checkbox" />
                <span>Usuario activo</span>
              </label>

              <div class="users-access-grid">
                <section class="users-access-panel">
                  <div class="users-access-header">
                    <p class="users-access-title">Roles asignados</p>
                    <p class="users-access-copy">Un usuario puede heredar permisos desde uno o varios roles.</p>
                  </div>

                  <div class="users-chip-grid">
                    <label v-for="role in catalog.roles" :key="role.id" class="users-chip">
                      <input
                        :checked="form.role_ids.includes(role.id)"
                        type="checkbox"
                        @change="toggleFormRole(role.id)"
                      />
                      <span>{{ role.nombre }}</span>
                    </label>
                  </div>
                </section>

                <section class="users-access-panel">
                  <div class="users-access-header">
                    <p class="users-access-title">Permisos directos por usuario</p>
                    <p class="users-access-copy">Sirven para excepciones puntuales adicionales al rol.</p>
                  </div>

                  <div class="users-permission-groups">
                    <section v-for="group in permissionsByModule" :key="group.moduleName" class="users-permission-group">
                      <header class="users-permission-group-header">
                        <p class="users-permission-group-title">{{ group.moduleName }}</p>
                      </header>

                      <div class="users-chip-grid">
                        <label v-for="permission in group.permissions" :key="permission.id" class="users-chip">
                          <input
                            :checked="form.permission_ids.includes(permission.id)"
                            type="checkbox"
                            @change="toggleFormPermission(permission.id)"
                          />
                          <span>{{ permission.nombre }}</span>
                        </label>
                      </div>
                    </section>
                  </div>
                </section>
              </div>

              <p v-if="userFeedback" class="users-feedback">{{ userFeedback }}</p>

              <div class="users-form-actions">
                <button type="button" class="btn btn--primary" :disabled="isSavingUser" @click="saveUser">
                  {{ isSavingUser ? 'Guardando...' : formMode === 'create' ? 'Crear usuario' : 'Guardar cambios' }}
                </button>
              </div>
            </div>
          </section>
        </div>
      </template>

      <template v-else-if="activeSection === 'roles'">
        <div class="users-role-layout">
          <section class="card card--acrylic tracking-card users-role-list-card" aria-label="Listado de roles">
            <header class="card__header">
              <div>
                <p class="card__header-title tracking-card-title">ROLES</p>
                <p class="users-card-copy">Selecciona un rol para revisar y ajustar su matriz de permisos.</p>
              </div>
            </header>

            <div class="card__body users-role-list">
              <button
                v-for="role in filteredRoles"
                :key="role.id"
                type="button"
                class="users-role-item"
                :class="{ 'users-role-item--active': selectedRoleId === role.id }"
                @click="selectRole(role.id)"
              >
                <span class="users-role-item-name">{{ role.nombre }}</span>
                <span class="users-role-item-code">{{ role.codigo }}</span>
              </button>
            </div>
          </section>

          <section class="card card--acrylic tracking-card users-role-card" aria-label="Permisos por rol">
            <header class="card__header tracking-card-header--space-between">
              <div>
                <p class="card__header-title tracking-card-title">PERMISOS POR ROL</p>
                <p class="users-card-copy">Ajusta la matriz base de permisos heredados por cada rol.</p>
              </div>

              <label class="tracking-field users-role-select">
                <span class="input-label">Rol</span>
                <select v-model="selectedRoleId" class="select select--sm">
                  <option v-for="role in catalog.roles" :key="role.id" :value="role.id">{{ role.nombre }}</option>
                </select>
              </label>
            </header>

            <div class="card__body users-role-body">
              <div v-if="selectedRole" class="users-role-summary">
                <p class="users-role-name">{{ selectedRole.nombre }}</p>
                <p class="users-role-copy">{{ selectedRole.descripcion || 'Sin descripcion registrada.' }}</p>
              </div>

              <div class="users-permission-groups">
                <section v-for="group in permissionsByModule" :key="group.moduleName" class="users-permission-group">
                  <header class="users-permission-group-header">
                    <p class="users-permission-group-title">{{ group.moduleName }}</p>
                  </header>

                  <div class="users-chip-grid">
                    <label v-for="permission in group.permissions" :key="permission.id" class="users-chip">
                      <input
                        :checked="rolePermissionDraft.includes(permission.id)"
                        type="checkbox"
                        @change="toggleRoleDraftPermission(permission.id)"
                      />
                      <span>{{ permission.nombre }}</span>
                    </label>
                  </div>
                </section>
              </div>

              <p v-if="roleFeedback" class="users-feedback">{{ roleFeedback }}</p>

              <div class="users-form-actions">
                <button type="button" class="btn btn--primary" :disabled="isSavingRole || !selectedRoleId" @click="saveRolePermissionMatrix">
                  {{ isSavingRole ? 'Guardando...' : 'Guardar permisos del rol' }}
                </button>
              </div>
            </div>
          </section>
        </div>
      </template>

      <template v-else>
        <section class="card card--acrylic tracking-card users-permissions-card" aria-label="Catalogo de permisos">
          <header class="card__header tracking-card-header--space-between">
            <div>
              <p class="card__header-title tracking-card-title">PERMISOS</p>
              <p class="users-card-copy">Vista general del catalogo de permisos disponible para el sistema.</p>
            </div>

            <label class="tracking-field users-role-select">
              <span class="input-label">Buscar permiso</span>
              <input
                v-model="permissionSearchTerm"
                class="input input--sm"
                type="text"
                placeholder="Codigo, nombre, accion o descripcion"
              />
            </label>
          </header>

          <div class="card__body users-role-body">
            <div class="users-permission-groups">
              <section v-for="group in filteredPermissionsByModule" :key="group.moduleName" class="users-permission-group">
                <header class="users-permission-group-header">
                  <p class="users-permission-group-title">{{ group.moduleName }}</p>
                </header>

                <div class="tracking-table-wrap">
                  <table class="table table--compact tracking-table tracking-table--borderless users-permission-table">
                    <thead>
                      <tr>
                        <th>Codigo</th>
                        <th>Nombre</th>
                        <th>Accion</th>
                        <th>Estado</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="permission in group.permissions" :key="permission.id">
                        <td>{{ permission.codigo }}</td>
                        <td>{{ permission.nombre }}</td>
                        <td>{{ permission.accion || '-' }}</td>
                        <td>
                          <span class="badge badge--sm" :class="permission.estado ? 'badge--success' : 'badge--danger'">
                            {{ permission.estado ? 'Activo' : 'Inactivo' }}
                          </span>
                        </td>
                      </tr>
                      <tr v-if="group.permissions.length === 0">
                        <td colspan="4" class="tracking-empty">Sin permisos en este modulo.</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </section>
            </div>
          </div>
        </section>
      </template>
    </section>
  </AppShell>
</template>
