<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import AppSidebar from '@/features/navigation/components/AppSidebar.vue'
import TrackingPageHeader from '@/features/dashboard/components/TrackingPageHeader.vue'
import PermissionsSubmodulePanel from '@/features/users/components/PermissionsSubmodulePanel.vue'
import RolesSubmodulePanel from '@/features/users/components/RolesSubmodulePanel.vue'
import UsersSubmodulePanel from '@/features/users/components/UsersSubmodulePanel.vue'
import {
  createPermission,
  createRole,
  createUser,
  fetchAccessCatalog,
  updatePermission,
  updateRole,
  updateUser,
  updateUserStatus,
} from '@/features/users/api/users.api'
import type {
  AccessPermission,
  AccessRole,
  AccessUser,
  PermissionPayload,
  RolePayload,
  UserPayload,
} from '@/features/users/types'
import AppShell from '@/shared/layouts/AppShell.vue'

type FeedbackTone = 'success' | 'warning' | 'danger' | 'accent'
type UserFieldKey = 'username' | 'name' | 'last_name' | 'email' | 'area'
type RoleFieldKey = 'codigo' | 'nombre'
type PermissionFieldKey = 'codigo' | 'nombre' | 'modulo' | 'accion'

const route = useRoute()
const router = useRouter()
const mobileBreakpoint = window.matchMedia('(max-width: 1080px)')

const isSidebarOpen = ref(false)
const isLoading = ref(true)
const loadError = ref('')
const userFeedback = ref('')
const roleFeedback = ref('')
const permissionFeedback = ref('')
const searchTerm = ref('')
const userRoleFilter = ref('')
const userStatusFilter = ref('')
const userPaginationPage = ref(1)
const userRolePaginationPage = ref(1)
const roleSearchTerm = ref('')
const permissionSearchTerm = ref('')
const selectedUserId = ref<string | null>(null)
const selectedRoleId = ref<string | null>(null)
const selectedPermissionId = ref<string | null>(null)
const formMode = ref<'create' | 'edit'>('create')
const roleFormMode = ref<'create' | 'edit'>('create')
const permissionFormMode = ref<'create' | 'edit'>('create')
const isSavingUser = ref(false)
const isSavingRole = ref(false)
const isSavingPermission = ref(false)
const userFeedbackTone = ref<FeedbackTone>('accent')
const roleFeedbackTone = ref<FeedbackTone>('accent')
const permissionFeedbackTone = ref<FeedbackTone>('accent')
const userValidationAttempted = ref(false)
const roleValidationAttempted = ref(false)
const permissionValidationAttempted = ref(false)
const toastQueue = ref<Array<{ id: number; title: string; message: string; tone: FeedbackTone }>>([])
let toastSequence = 0

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

const roleForm = reactive<RolePayload>({
  codigo: '',
  nombre: '',
  descripcion: '',
  estado: true,
  permission_ids: [],
  user_ids: [],
})

const permissionForm = reactive<PermissionPayload>({
  codigo: '',
  nombre: '',
  modulo: '',
  accion: '',
  descripcion: '',
  estado: true,
  role_ids: [],
  user_ids: [],
})

const selectedRole = computed(() => catalog.roles.find((role) => role.id === selectedRoleId.value) ?? null)
const selectedPermission = computed(() => catalog.permissions.find((permission) => permission.id === selectedPermissionId.value) ?? null)

function getRoleAssignedUsers(roleId: string): AccessUser[] {
  return catalog.users.filter((user) => user.role_ids.includes(roleId))
}

const summaryCards = computed(() => {
  if (activeSection.value === 'roles' && selectedRole.value) {
    const assignedUsers = getRoleAssignedUsers(selectedRole.value.id)
    const activeAssignedUsers = assignedUsers.filter((user) => user.is_active).length

    return [
      { value: assignedUsers.length, label: 'Usuarios del rol' },
      { value: activeAssignedUsers, label: 'Usuarios activos' },
      { value: selectedRole.value.permission_ids.length, label: 'Permisos base' },
      { value: selectedRole.value.estado ? 'Activo' : 'Inactivo', label: 'Estado del rol' },
    ]
  }

  if (activeSection.value === 'permisos' && selectedPermission.value) {
    return [
      { value: selectedPermission.value.role_ids.length, label: 'Roles asociados' },
      { value: selectedPermission.value.user_ids.length, label: 'Usuarios directos' },
      { value: selectedPermission.value.modulo || 'General', label: 'Modulo del permiso' },
      { value: selectedPermission.value.estado ? 'Activo' : 'Inactivo', label: 'Estado del permiso' },
    ]
  }

  return [
    { value: catalog.users.length, label: 'Usuarios registrados' },
    { value: catalog.users.filter((user) => user.is_active).length, label: 'Usuarios activos' },
    { value: catalog.roles.length, label: 'Roles configurados' },
    { value: catalog.permissions.length, label: 'Permisos disponibles' },
  ]
})

const activeSection = computed<'usuarios' | 'roles' | 'permisos'>(() => {
  const section = String(route.meta.userSection ?? 'usuarios').trim()
  return section === 'roles' || section === 'permisos' ? section : 'usuarios'
})

const userViewMode = computed<'list' | 'create' | 'edit'>(() => {
  const mode = String(route.meta.userMode ?? 'list').trim()
  return mode === 'create' || mode === 'edit' ? mode : 'list'
})

const userStep = computed<'datos' | 'roles' | 'permisos' | 'resumen'>(() => {
  const step = String(route.meta.userStep ?? 'datos').trim()
  return step === 'roles' || step === 'permisos' || step === 'resumen' ? step : 'datos'
})

const isUserWizard = computed(() => activeSection.value === 'usuarios' && userViewMode.value !== 'list')

const heroDescription = computed(() => {
  if (activeSection.value === 'roles') {
    return 'Administra los roles del sistema, sus permisos base y los usuarios que los heredan.'
  }

  if (activeSection.value === 'permisos') {
    return 'Gestiona el catalogo de permisos y distribuyelo por roles o usuarios puntuales.'
  }

  if (isUserWizard.value) {
    return 'Completa el flujo por pasos para registrar o actualizar un usuario sin saturar la vista principal.'
  }

  return 'Consulta datos del usuario, edita su ficha y controla su acceso operativo.'
})

const filteredUsers = computed(() => {
  const query = searchTerm.value.trim().toLowerCase()
  const roleId = userRoleFilter.value.trim()
  const status = userStatusFilter.value.trim()

  return catalog.users.filter((user) => {
    const matchesQuery =
      !query || [user.username, user.fullname, user.email, user.area].some((value) => value.toLowerCase().includes(query))
    const matchesRole = !roleId || user.role_ids.includes(roleId)
    const matchesStatus =
      !status || (status === 'active' && user.is_active) || (status === 'inactive' && !user.is_active)

    return matchesQuery && matchesRole && matchesStatus
  })
})

const sortedUsers = computed(() =>
  [...catalog.users].sort((left, right) => (left.fullname || left.username).localeCompare(right.fullname || right.username)),
)

const userRoleOptions = computed(() =>
  [...catalog.roles].sort((left, right) => left.nombre.localeCompare(right.nombre)),
)

const userPageSize = 6

const userPaginationTotalPages = computed(() => Math.max(1, Math.ceil(filteredUsers.value.length / userPageSize)))

const paginatedUsers = computed(() => {
  const start = (userPaginationPage.value - 1) * userPageSize
  return filteredUsers.value.slice(start, start + userPageSize)
})

const userPaginationPages = computed(() =>
  Array.from({ length: userPaginationTotalPages.value }, (_, index) => index + 1),
)

watch([searchTerm, userRoleFilter, userStatusFilter], () => {
  userPaginationPage.value = 1
})

watch(userPaginationTotalPages, (totalPages) => {
  if (userPaginationPage.value > totalPages) {
    userPaginationPage.value = totalPages
  }
})

const filteredRoles = computed(() => {
  const query = roleSearchTerm.value.trim().toLowerCase()
  const roles = [...catalog.roles]

  const filtered = !query
    ? roles
    : roles.filter((role) =>
        [role.codigo, role.nombre, role.descripcion].join(' ').toLowerCase().includes(query),
      )

  return filtered.sort((left, right) => {
    const userCountDifference = getRoleAssignedUsers(right.id).length - getRoleAssignedUsers(left.id).length
    if (userCountDifference !== 0) {
      return userCountDifference
    }

    return left.nombre.localeCompare(right.nombre)
  })
})

const userRolePageSize = 9

const userRolePaginationTotalPages = computed(() => Math.max(1, Math.ceil(filteredRoles.value.length / userRolePageSize)))

const paginatedUserWizardRoles = computed(() => {
  const start = (userRolePaginationPage.value - 1) * userRolePageSize
  return filteredRoles.value.slice(start, start + userRolePageSize)
})

const userRolePaginationPages = computed(() =>
  Array.from({ length: userRolePaginationTotalPages.value }, (_, index) => index + 1),
)

watch(filteredRoles, () => {
  userRolePaginationPage.value = 1
})

watch(userRolePaginationTotalPages, (totalPages) => {
  if (userRolePaginationPage.value > totalPages) {
    userRolePaginationPage.value = totalPages
  }
})

const filteredPermissions = computed(() => {
  const query = permissionSearchTerm.value.trim().toLowerCase()
  const permissions = [...catalog.permissions]

  const filtered = !query
    ? permissions
    : permissions.filter((permission) =>
        [permission.codigo, permission.nombre, permission.modulo, permission.accion, permission.descripcion]
          .join(' ')
          .toLowerCase()
          .includes(query),
      )

  return filtered.sort((left, right) => {
    const associationDiff = right.role_ids.length + right.user_ids.length - (left.role_ids.length + left.user_ids.length)
    if (associationDiff !== 0) {
      return associationDiff
    }

    return [left.modulo, left.nombre].join(' ').localeCompare([right.modulo, right.nombre].join(' '))
  })
})

const selectedUser = computed(() => catalog.users.find((user) => user.id === selectedUserId.value) ?? null)

const selectedFormRoles = computed(() =>
  catalog.roles.filter((role) => form.role_ids.includes(role.id)).sort((left, right) => left.nombre.localeCompare(right.nombre)),
)

const inheritedPermissionIds = computed(() => {
  const ids = selectedFormRoles.value.flatMap((role) => role.permission_ids)
  return [...new Set(ids)]
})

const directPermissionIds = computed(() =>
  form.permission_ids.filter((permissionId) => !inheritedPermissionIds.value.includes(permissionId)),
)

const effectivePermissionIdsPreview = computed(() => [...new Set([...inheritedPermissionIds.value, ...directPermissionIds.value])])

const permissionsByModule = computed(() => {
  const grouped = new Map<string, AccessPermission[]>()

  for (const permission of catalog.permissions) {
    const moduleName = permission.modulo || 'General'
    const bucket = grouped.get(moduleName) ?? []
    bucket.push(permission)
    grouped.set(moduleName, bucket)
  }

  return [...grouped.entries()]
    .map(([moduleName, permissions]) => ({
      moduleName,
      permissions: [...permissions].sort((left, right) => left.nombre.localeCompare(right.nombre)),
    }))
    .sort((left, right) => left.moduleName.localeCompare(right.moduleName))
})

const userWizardSteps = [
  { id: 'datos', label: 'Datos' },
  { id: 'roles', label: 'Roles' },
  { id: 'permisos', label: 'Permisos' },
  { id: 'resumen', label: 'Resumen' },
] as const

const currentWizardStepIndex = computed(() =>
  Math.max(0, userWizardSteps.findIndex((step) => step.id === userStep.value)),
)

const wizardTitle = computed(() => (userViewMode.value === 'create' ? 'NUEVO USUARIO' : 'EDITAR USUARIO'))

const wizardPrimaryLabel = computed(() => {
  if (userStep.value === 'resumen') {
    return isSavingUser.value
      ? 'Guardando...'
      : userViewMode.value === 'create'
        ? 'Crear usuario'
        : 'Guardar cambios'
  }

  return 'Siguiente'
})

const wizardSecondaryLabel = computed(() => (currentWizardStepIndex.value === 0 ? 'Cancelar' : 'Anterior'))

const userFormErrors = computed<Record<UserFieldKey, string>>(() => ({
  username: form.username.trim() ? '' : 'Ingresa el username del usuario.',
  name: form.name.trim() ? '' : 'Ingresa los nombres.',
  last_name: form.last_name.trim() ? '' : 'Ingresa los apellidos.',
  email: !form.email.trim()
    ? 'Ingresa el correo corporativo.'
    : /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email.trim())
      ? ''
      : 'Ingresa un correo valido.',
  area: form.area.trim() ? '' : 'Ingresa el area del usuario.',
}))

const roleFormErrors = computed<Record<RoleFieldKey, string>>(() => ({
  codigo: roleForm.codigo.trim() ? '' : 'Ingresa el codigo del rol.',
  nombre: roleForm.nombre.trim() ? '' : 'Ingresa el nombre del rol.',
}))

const permissionFormErrors = computed<Record<PermissionFieldKey, string>>(() => ({
  codigo: permissionForm.codigo.trim() ? '' : 'Ingresa el codigo del permiso.',
  nombre: permissionForm.nombre.trim() ? '' : 'Ingresa el nombre del permiso.',
  modulo: permissionForm.modulo.trim() ? '' : 'Ingresa el modulo asociado.',
  accion: permissionForm.accion.trim() ? '' : 'Ingresa la accion del permiso.',
}))

function pushToast(title: string, message: string, tone: FeedbackTone): void {
  const id = ++toastSequence
  toastQueue.value = [...toastQueue.value, { id, title, message, tone }]
  window.setTimeout(() => {
    toastQueue.value = toastQueue.value.filter((toast) => toast.id !== id)
  }, 5000)
}

function dismissToast(toastId: number): void {
  toastQueue.value = toastQueue.value.filter((toast) => toast.id !== toastId)
}

function hasUserFormErrors(): boolean {
  return Object.values(userFormErrors.value).some(Boolean)
}

function getFirstUserFormError(): string {
  return Object.values(userFormErrors.value).find(Boolean) ?? 'Corrige los campos obligatorios antes de continuar.'
}

function hasRoleFormErrors(): boolean {
  return Object.values(roleFormErrors.value).some(Boolean)
}

function hasPermissionFormErrors(): boolean {
  return Object.values(permissionFormErrors.value).some(Boolean)
}

function isDatosStepComplete(): boolean {
  return !hasUserFormErrors()
}

function isRolesStepComplete(): boolean {
  return form.role_ids.length > 0
}

function isPermisosStepComplete(): boolean {
  return true
}

function isWizardStepComplete(stepId: (typeof userWizardSteps)[number]['id']): boolean {
  if (stepId === 'datos') {
    return isDatosStepComplete()
  }

  if (stepId === 'roles') {
    return isRolesStepComplete()
  }

  if (stepId === 'permisos') {
    return isPermisosStepComplete()
  }

  return isDatosStepComplete() && isRolesStepComplete() && isPermisosStepComplete()
}

function canAccessWizardStep(stepIndex: number): boolean {
  if (stepIndex <= 0) {
    return true
  }

  for (let index = 0; index < stepIndex; index += 1) {
    const previousStep = userWizardSteps[index]
    if (previousStep && !isWizardStepComplete(previousStep.id)) {
      return false
    }
  }

  return true
}

function getWizardBlockMessage(stepId: (typeof userWizardSteps)[number]['id']): string {
  if (stepId === 'roles') {
    return 'Completa primero los datos base del usuario antes de pasar a roles.'
  }

  if (stepId === 'permisos') {
    return 'Define al menos un rol antes de pasar a permisos.'
  }

  return 'Completa los pasos previos antes de revisar el resumen final.'
}

function groupPermissionsByIds(permissionIds: string[]) {
  const permissionSet = new Set(permissionIds)

  return permissionsByModule.value
    .map((group) => ({
      moduleName: group.moduleName,
      permissions: group.permissions.filter((permission) => permissionSet.has(permission.id)),
    }))
    .filter((group) => group.permissions.length > 0)
}

const inheritedPermissionsByModule = computed(() => groupPermissionsByIds(inheritedPermissionIds.value))
const effectivePermissionsByModule = computed(() => groupPermissionsByIds(effectivePermissionIdsPreview.value))

const availableDirectPermissionsByModule = computed(() => {
  const inheritedSet = new Set(inheritedPermissionIds.value)

  return permissionsByModule.value
    .map((group) => ({
      moduleName: group.moduleName,
      permissions: group.permissions.filter((permission) => !inheritedSet.has(permission.id)),
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
  userValidationAttempted.value = false
}

function resetRoleForm(): void {
  roleForm.codigo = ''
  roleForm.nombre = ''
  roleForm.descripcion = ''
  roleForm.estado = true
  roleForm.permission_ids = []
  roleForm.user_ids = []
  roleValidationAttempted.value = false
}

function resetPermissionForm(): void {
  permissionForm.codigo = ''
  permissionForm.nombre = ''
  permissionForm.modulo = ''
  permissionForm.accion = ''
  permissionForm.descripcion = ''
  permissionForm.estado = true
  permissionForm.role_ids = []
  permissionForm.user_ids = []
  permissionValidationAttempted.value = false
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

function syncFormWithRole(role: AccessRole): void {
  roleForm.codigo = role.codigo
  roleForm.nombre = role.nombre
  roleForm.descripcion = role.descripcion
  roleForm.estado = role.estado
  roleForm.permission_ids = [...role.permission_ids]
  roleForm.user_ids = [...role.user_ids]
}

function syncFormWithPermission(permission: AccessPermission): void {
  permissionForm.codigo = permission.codigo
  permissionForm.nombre = permission.nombre
  permissionForm.modulo = permission.modulo
  permissionForm.accion = permission.accion
  permissionForm.descripcion = permission.descripcion
  permissionForm.estado = permission.estado
  permissionForm.role_ids = [...permission.role_ids]
  permissionForm.user_ids = [...permission.user_ids]
}

function beginCreateUser(): void {
  selectedUserId.value = null
  formMode.value = 'create'
  userFeedback.value = ''
  userFeedbackTone.value = 'accent'
  resetForm()
  void router.push('/usuarios/usuarios/nuevo/datos')
}

function beginEditUser(user: AccessUser): void {
  selectedUserId.value = user.id
  formMode.value = 'edit'
  userFeedback.value = ''
  userFeedbackTone.value = 'accent'
  userValidationAttempted.value = false
  syncFormWithUser(user)
  void router.push(`/usuarios/usuarios/${user.id}/editar/datos`)
}

function openUserDetail(user: AccessUser): void {
  selectedUserId.value = user.id
}

function cancelUserWizard(): void {
  userFeedback.value = ''
  userFeedbackTone.value = 'accent'
  if (userViewMode.value === 'create') {
    resetForm()
  }
  void router.push('/usuarios/usuarios')
}

function buildUserWizardPath(stepId: (typeof userWizardSteps)[number]['id']): string {
  if (userViewMode.value === 'edit' && route.params.userId) {
    return `/usuarios/usuarios/${String(route.params.userId)}/editar/${stepId}`
  }

  return `/usuarios/usuarios/nuevo/${stepId}`
}

function goToUserWizardStep(stepId: (typeof userWizardSteps)[number]['id']): void {
  if (!isUserWizard.value) {
    return
  }

  const targetIndex = userWizardSteps.findIndex((step) => step.id === stepId)
  if (targetIndex === -1) {
    return
  }

  if (!canAccessWizardStep(targetIndex)) {
    userFeedbackTone.value = 'warning'
    userFeedback.value = getWizardBlockMessage(stepId)
    pushToast('Validacion', userFeedback.value, 'warning')
    return
  }

  void router.push(buildUserWizardPath(stepId))
}

function goToPreviousWizardStep(): void {
  if (currentWizardStepIndex.value === 0) {
    cancelUserWizard()
    return
  }

  const previousStep = userWizardSteps[currentWizardStepIndex.value - 1]
  if (previousStep) {
    goToUserWizardStep(previousStep.id)
  }
}

async function handleWizardPrimaryAction(): Promise<void> {
  userFeedback.value = ''

  if (userStep.value === 'datos' && !isDatosStepComplete()) {
    userValidationAttempted.value = true
    userFeedbackTone.value = 'warning'
    userFeedback.value = getFirstUserFormError()
    pushToast('Validacion', userFeedback.value, 'warning')
    return
  }

  if (userStep.value === 'roles' && !isRolesStepComplete()) {
    userFeedbackTone.value = 'warning'
    userFeedback.value = 'Selecciona al menos un rol antes de continuar.'
    pushToast('Validacion', userFeedback.value, 'warning')
    return
  }

  if (userStep.value === 'resumen') {
    await saveUser()
    return
  }

  const nextStep = userWizardSteps[currentWizardStepIndex.value + 1]
  if (nextStep) {
    goToUserWizardStep(nextStep.id)
  }
}

function startCreateRole(): void {
  selectedRoleId.value = null
  roleFormMode.value = 'create'
  roleFeedback.value = ''
  roleFeedbackTone.value = 'accent'
  resetRoleForm()
}

function startCreatePermission(): void {
  selectedPermissionId.value = null
  permissionFormMode.value = 'create'
  permissionFeedback.value = ''
  permissionFeedbackTone.value = 'accent'
  resetPermissionForm()
}

function selectRole(role: AccessRole): void {
  selectedRoleId.value = role.id
  roleFormMode.value = 'edit'
  roleFeedback.value = ''
  roleFeedbackTone.value = 'accent'
  roleValidationAttempted.value = false
  syncFormWithRole(role)
}

function selectPermission(permission: AccessPermission): void {
  selectedPermissionId.value = permission.id
  permissionFormMode.value = 'edit'
  permissionFeedback.value = ''
  permissionFeedbackTone.value = 'accent'
  permissionValidationAttempted.value = false
  syncFormWithPermission(permission)
}

function syncUserWizardFromRoute(): void {
  if (activeSection.value !== 'usuarios') {
    return
  }

  if (userViewMode.value === 'list') {
    return
  }

  if (userViewMode.value === 'create') {
    if (formMode.value !== 'create') {
      formMode.value = 'create'
      resetForm()
    }
    userFeedback.value = ''
    userFeedbackTone.value = 'accent'
    return
  }

  const routeUserId = String(route.params.userId ?? '').trim()
  if (!routeUserId) {
    return
  }

  selectedUserId.value = routeUserId
  formMode.value = 'edit'
  userFeedback.value = ''
  userFeedbackTone.value = 'accent'

  const existingUser = catalog.users.find((user) => user.id === routeUserId)
  if (existingUser) {
    syncFormWithUser(existingUser)
  }
}

async function loadModuleData(): Promise<void> {
  isLoading.value = true
  loadError.value = ''

  try {
    const response = await fetchAccessCatalog()
    catalog.users = response.users
    catalog.roles = response.roles
    catalog.permissions = response.permissions

    if (selectedUserId.value && !isUserWizard.value) {
      const refreshedUser = response.users.find((user) => user.id === selectedUserId.value)
      if (!refreshedUser) {
        selectedUserId.value = null
      }
    }

    if (selectedRoleId.value) {
      const refreshedRole = response.roles.find((role) => role.id === selectedRoleId.value)
      refreshedRole ? syncFormWithRole(refreshedRole) : startCreateRole()
    }

    if (selectedPermissionId.value) {
      const refreshedPermission = response.permissions.find((permission) => permission.id === selectedPermissionId.value)
      refreshedPermission ? syncFormWithPermission(refreshedPermission) : startCreatePermission()
    }

    syncUserWizardFromRoute()
  } catch (error) {
    loadError.value = error instanceof Error ? error.message : 'No se pudo cargar el modulo de usuarios'
    pushToast('Modulo usuarios', loadError.value, 'danger')
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
      permission_ids: [...directPermissionIds.value],
    }

    const result =
      formMode.value === 'create'
        ? await createUser(payload)
        : await updateUser(selectedUserId.value ?? '', payload)

    userFeedbackTone.value = 'success'
    userFeedback.value = result.message
    pushToast(userViewMode.value === 'create' ? 'Usuario creado' : 'Usuario actualizado', result.message, 'success')
    await loadModuleData()

    if (result.user) {
      selectedUserId.value = result.user.id
      formMode.value = 'edit'
      syncFormWithUser(result.user)
      void router.push('/usuarios/usuarios')
    }
  } catch (error) {
    userFeedbackTone.value = 'danger'
    userFeedback.value = error instanceof Error ? error.message : 'No se pudo guardar el usuario'
    pushToast('Error al guardar', userFeedback.value, 'danger')
  } finally {
    isSavingUser.value = false
  }
}

async function toggleUserActive(user: AccessUser): Promise<void> {
  userFeedback.value = ''

  try {
    const result = await updateUserStatus(user.id, !user.is_active)
    userFeedbackTone.value = 'success'
    userFeedback.value = result.message
    pushToast('Estado actualizado', result.message, 'success')
    await loadModuleData()
  } catch (error) {
    userFeedbackTone.value = 'danger'
    userFeedback.value = error instanceof Error ? error.message : 'No se pudo actualizar el estado'
    pushToast('Error de estado', userFeedback.value, 'danger')
  }
}

async function saveRole(): Promise<void> {
  isSavingRole.value = true
  roleFeedback.value = ''
  roleValidationAttempted.value = true

  if (hasRoleFormErrors()) {
    roleFeedbackTone.value = 'warning'
    roleFeedback.value = 'Completa codigo y nombre antes de guardar el rol.'
    pushToast('Validacion', roleFeedback.value, 'warning')
    isSavingRole.value = false
    return
  }

  try {
    const payload: RolePayload = {
      codigo: roleForm.codigo.trim(),
      nombre: roleForm.nombre.trim(),
      descripcion: roleForm.descripcion.trim(),
      estado: roleForm.estado,
      permission_ids: [...roleForm.permission_ids],
      user_ids: [...roleForm.user_ids],
    }

    const result =
      roleFormMode.value === 'create'
        ? await createRole(payload)
        : await updateRole(selectedRoleId.value ?? '', payload)

    roleFeedbackTone.value = 'success'
    roleFeedback.value = result.message
    pushToast(roleFormMode.value === 'create' ? 'Rol creado' : 'Rol actualizado', result.message, 'success')
    await loadModuleData()

    if (result.role) {
      selectedRoleId.value = result.role.id
      roleFormMode.value = 'edit'
      syncFormWithRole(result.role)
    }
  } catch (error) {
    roleFeedbackTone.value = 'danger'
    roleFeedback.value = error instanceof Error ? error.message : 'No se pudo guardar el rol'
    pushToast('Error al guardar rol', roleFeedback.value, 'danger')
  } finally {
    isSavingRole.value = false
  }
}

async function savePermission(): Promise<void> {
  isSavingPermission.value = true
  permissionFeedback.value = ''
  permissionValidationAttempted.value = true

  if (hasPermissionFormErrors()) {
    permissionFeedbackTone.value = 'warning'
    permissionFeedback.value = 'Completa codigo, nombre, modulo y accion antes de guardar el permiso.'
    pushToast('Validacion', permissionFeedback.value, 'warning')
    isSavingPermission.value = false
    return
  }

  try {
    const payload: PermissionPayload = {
      codigo: permissionForm.codigo.trim(),
      nombre: permissionForm.nombre.trim(),
      modulo: permissionForm.modulo.trim(),
      accion: permissionForm.accion.trim(),
      descripcion: permissionForm.descripcion.trim(),
      estado: permissionForm.estado,
      role_ids: [...permissionForm.role_ids],
      user_ids: [...permissionForm.user_ids],
    }

    const result =
      permissionFormMode.value === 'create'
        ? await createPermission(payload)
        : await updatePermission(selectedPermissionId.value ?? '', payload)

    permissionFeedbackTone.value = 'success'
    permissionFeedback.value = result.message
    pushToast(permissionFormMode.value === 'create' ? 'Permiso creado' : 'Permiso actualizado', result.message, 'success')
    await loadModuleData()

    if (result.permission) {
      selectedPermissionId.value = result.permission.id
      permissionFormMode.value = 'edit'
      syncFormWithPermission(result.permission)
    }
  } catch (error) {
    permissionFeedbackTone.value = 'danger'
    permissionFeedback.value = error instanceof Error ? error.message : 'No se pudo guardar el permiso'
    pushToast('Error al guardar permiso', permissionFeedback.value, 'danger')
  } finally {
    isSavingPermission.value = false
  }
}

watch(
  () => route.fullPath,
  () => {
    syncUserWizardFromRoute()
  },
  { immediate: true },
)

onMounted(() => {
  if (mobileBreakpoint.matches) {
    closeSidebar()
  }

  mobileBreakpoint.addEventListener('change', handleViewportChange)
  void loadModuleData()
  startCreateRole()
  startCreatePermission()
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
      <div v-if="toastQueue.length" class="toast-container" aria-live="polite" aria-atomic="true">
        <article
          v-for="toast in toastQueue"
          :key="toast.id"
          class="toast"
          :class="`toast--${toast.tone}`"
          role="status"
        >
          <div class="toast__icon" aria-hidden="true">
            <span v-if="toast.tone === 'success'">✓</span>
            <span v-else-if="toast.tone === 'warning'">!</span>
            <span v-else-if="toast.tone === 'danger'">×</span>
            <span v-else>i</span>
          </div>
          <div class="toast__content">
            <div class="toast__title">{{ toast.title }}</div>
            <div class="toast__message">{{ toast.message }}</div>
          </div>
          <button type="button" class="toast__close" aria-label="Cerrar notificacion" @click="dismissToast(toast.id)">×</button>
          <span class="toast__progress" aria-hidden="true" />
        </article>
      </div>

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

      <header class="users-hero">
        <div class="users-hero-copy">
          <TrackingPageHeader />
          <p class="users-hero-text">{{ heroDescription }}</p>
        </div>
      </header>

      <div
        v-if="!(activeSection === 'usuarios' && isUserWizard)"
        class="users-summary-grid"
        :class="{ 'users-summary-grid--compact': !isUserWizard }"
      >
        <article v-for="card in summaryCards" :key="card.label" class="card card--acrylic tracking-card users-summary-card">
          <div class="card__body">
            <p class="users-summary-value">{{ card.value }}</p>
            <p class="users-summary-label">{{ card.label }}</p>
          </div>
        </article>
      </div>

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
        <UsersSubmodulePanel
          :search-term="searchTerm"
          :user-role-filter="userRoleFilter"
          :user-status-filter="userStatusFilter"
          :user-role-options="userRoleOptions"
          :filtered-users="paginatedUsers"
          :user-pagination-page="userPaginationPage"
          :user-pagination-pages="userPaginationPages"
          :user-pagination-total-pages="userPaginationTotalPages"
          :user-pagination-total-items="filteredUsers.length"
          :selected-user-id="selectedUserId"
          :selected-user="selectedUser"
          :is-user-wizard="isUserWizard"
          :wizard-title="wizardTitle"
          :current-wizard-step-index="currentWizardStepIndex"
          :user-wizard-steps="userWizardSteps"
          :user-step="userStep"
          :user-view-mode="userViewMode"
          :form-mode="formMode"
          :form="form"
          :selected-form-roles="selectedFormRoles"
          :filtered-roles="paginatedUserWizardRoles"
          :role-pagination-page="userRolePaginationPage"
          :role-pagination-pages="userRolePaginationPages"
          :role-pagination-total-pages="userRolePaginationTotalPages"
          :role-pagination-total-items="filteredRoles.length"
          :inherited-permission-ids="inheritedPermissionIds"
          :direct-permission-ids="directPermissionIds"
          :effective-permission-ids-preview="effectivePermissionIdsPreview"
          :available-direct-permissions-by-module="availableDirectPermissionsByModule"
          :effective-permissions-by-module="effectivePermissionsByModule"
          :user-feedback="userFeedback"
          :user-feedback-tone="userFeedbackTone"
          :user-validation-attempted="userValidationAttempted"
          :user-form-errors="userFormErrors"
          :is-saving-user="isSavingUser"
          :wizard-primary-label="wizardPrimaryLabel"
          :wizard-secondary-label="wizardSecondaryLabel"
          :describe-user-roles="describeUserRoles"
          :describe-effective-permission-count="describeEffectivePermissionCount"
          @update:search-term="searchTerm = $event"
          @update:user-role-filter="userRoleFilter = $event"
          @update:user-status-filter="userStatusFilter = $event"
          @update:user-pagination-page="userPaginationPage = $event"
          @update:role-pagination-page="userRolePaginationPage = $event"
          @create-user="beginCreateUser"
          @edit-user="beginEditUser"
          @open-user-detail="openUserDetail"
          @toggle-user-active="toggleUserActive"
          @cancel-user-wizard="cancelUserWizard"
          @previous-wizard-step="goToPreviousWizardStep"
          @primary-wizard-action="handleWizardPrimaryAction"
          @goto-wizard-step="goToUserWizardStep"
        />
      </template>

      <template v-else-if="activeSection === 'roles'">
        <RolesSubmodulePanel
          :role-search-term="roleSearchTerm"
          :filtered-roles="filteredRoles"
          :selected-role-id="selectedRoleId"
          :role-form-mode="roleFormMode"
          :role-form="roleForm"
          :sorted-users="sortedUsers"
          :role-options="userRoleOptions"
          :permissions-by-module="permissionsByModule"
          :role-feedback="roleFeedback"
          :role-feedback-tone="roleFeedbackTone"
          :role-validation-attempted="roleValidationAttempted"
          :role-form-errors="roleFormErrors"
          :is-saving-role="isSavingRole"
          @update:role-search-term="roleSearchTerm = $event"
          @select-role="selectRole"
          @create-role="startCreateRole"
          @save-role="saveRole"
        />
      </template>

      <template v-else>
        <PermissionsSubmodulePanel
          :permission-search-term="permissionSearchTerm"
          :filtered-permissions="filteredPermissions"
          :filtered-roles="filteredRoles"
          :role-options="userRoleOptions"
          :sorted-users="sortedUsers"
          :selected-permission-id="selectedPermissionId"
          :permission-form-mode="permissionFormMode"
          :permission-form="permissionForm"
          :permission-feedback="permissionFeedback"
          :permission-feedback-tone="permissionFeedbackTone"
          :permission-validation-attempted="permissionValidationAttempted"
          :permission-form-errors="permissionFormErrors"
          :is-saving-permission="isSavingPermission"
          @update:permission-search-term="permissionSearchTerm = $event"
          @select-permission="selectPermission"
          @create-permission="startCreatePermission"
          @save-permission="savePermission"
        />
      </template>
    </section>
  </AppShell>
</template>
