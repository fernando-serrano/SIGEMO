import { computed, reactive, ref, type Ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import type { AccessUser, UserPayload } from '../types'
import { createUser, updateUser, updateUserStatus } from '../api/users.api'

export type FeedbackTone = 'success' | 'warning' | 'danger' | 'accent'
export type UserFieldKey = 'username' | 'name' | 'last_name' | 'email' | 'area'

export function useUserForm(
  catalogUsers: Ref<AccessUser[]>,
  loadModuleData: () => Promise<void>,
  pushToast: (title: string, message: string, tone: FeedbackTone) => void,
) {
  const router = useRouter()
  const route = useRoute()

  const formMode = ref<'create' | 'edit'>('create')
  const isSavingUser = ref(false)
  const userFeedback = ref('')
  const userFeedbackTone = ref<FeedbackTone>('accent')
  const userValidationAttempted = ref(false)
  const selectedUserId = ref<string | null>(null)

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

  const userWizardSteps = [
    { id: 'datos', label: 'Datos' },
    { id: 'roles', label: 'Roles' },
    { id: 'permisos', label: 'Permisos' },
    { id: 'resumen', label: 'Resumen' },
  ] as const

  const userViewMode = computed<'list' | 'create' | 'edit'>(() => {
    const mode = String(route.meta.userMode ?? 'list').trim()
    return mode === 'create' || mode === 'edit' ? mode : 'list'
  })

  const userStep = computed<'datos' | 'roles' | 'permisos' | 'resumen'>(() => {
    const step = String(route.meta.userStep ?? 'datos').trim()
    return step === 'roles' || step === 'permisos' || step === 'resumen' ? step : 'datos'
  })

  const isUserWizard = computed(() => userViewMode.value !== 'list')

  const currentWizardStepIndex = computed(() =>
    Math.max(0, userWizardSteps.findIndex((step) => step.id === userStep.value)),
  )

  const wizardTitle = computed(() =>
    userViewMode.value === 'create' ? 'Nuevo Usuario' : 'Editar Usuario',
  )

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

  const wizardSecondaryLabel = computed(() =>
    currentWizardStepIndex.value === 0 ? 'Cancelar' : 'Anterior',
  )

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

  function hasUserFormErrors(): boolean {
    return Object.values(userFormErrors.value).some(Boolean)
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
    if (stepId === 'datos') return isDatosStepComplete()
    if (stepId === 'roles') return isRolesStepComplete()
    if (stepId === 'permisos') return isPermisosStepComplete()
    return isDatosStepComplete() && isRolesStepComplete() && isPermisosStepComplete()
  }

  function canAccessWizardStep(stepIndex: number): boolean {
    if (stepIndex <= 0) return true
    for (let index = 0; index < stepIndex; index += 1) {
      const previousStep = userWizardSteps[index]
      if (previousStep && !isWizardStepComplete(previousStep.id)) {
        return false
      }
    }
    return true
  }

  function getWizardBlockMessage(stepId: (typeof userWizardSteps)[number]['id']): string {
    if (stepId === 'roles') return 'Completa primero los datos base del usuario antes de pasar a roles.'
    if (stepId === 'permisos') return 'Define al menos un rol antes de pasar a permisos.'
    return 'Completa los pasos previos antes de revisar el resumen final.'
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
    if (!isUserWizard.value) return

    const targetIndex = userWizardSteps.findIndex((step) => step.id === stepId)
    if (targetIndex === -1) return

    if (!canAccessWizardStep(targetIndex)) {
      userFeedbackTone.value = 'warning'
      userFeedback.value = getWizardBlockMessage(stepId)
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
      userFeedback.value = 'Corrige los campos obligatorios antes de continuar.'
      return
    }

    if (userStep.value === 'roles' && !isRolesStepComplete()) {
      userFeedbackTone.value = 'warning'
      userFeedback.value = 'Selecciona al menos un rol antes de continuar.'
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

      userFeedbackTone.value = 'success'
      userFeedback.value = result.message
      pushToast(
        userViewMode.value === 'create' ? 'Usuario creado' : 'Usuario actualizado',
        result.message,
        'success',
      )
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

  function syncUserWizardFromRoute(): void {
    if (userViewMode.value === 'list') return

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
    if (!routeUserId) return

    selectedUserId.value = routeUserId
    formMode.value = 'edit'
    userFeedback.value = ''
    userFeedbackTone.value = 'accent'

    const existingUser = catalogUsers.value.find((user) => user.id === routeUserId)
    if (existingUser) {
      syncFormWithUser(existingUser)
    }
  }

  return {
    formMode,
    isSavingUser,
    userFeedback,
    userFeedbackTone,
    userValidationAttempted,
    selectedUserId,
    form,
    userViewMode,
    userStep,
    isUserWizard,
    currentWizardStepIndex,
    wizardTitle,
    wizardPrimaryLabel,
    wizardSecondaryLabel,
    userFormErrors,
    userWizardSteps,
    hasUserFormErrors,
    isDatosStepComplete,
    isRolesStepComplete,
    isWizardStepComplete,
    canAccessWizardStep,
    resetForm,
    syncFormWithUser,
    beginCreateUser,
    beginEditUser,
    cancelUserWizard,
    goToUserWizardStep,
    goToPreviousWizardStep,
    handleWizardPrimaryAction,
    saveUser,
    toggleUserActive,
    syncUserWizardFromRoute,
  }
}
