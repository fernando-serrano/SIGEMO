import { computed, reactive, ref, type Ref } from 'vue'
import { useRouter } from 'vue-router'
import type { AccessRole, RolePayload } from '../types'
import { createRole, updateRole } from '../api/users.api'

export type RoleFieldKey = 'codigo' | 'nombre'

export function useRoleForm(
  catalogRoles: Ref<AccessRole[]>,
  loadModuleData: () => Promise<void>,
  pushToast: (title: string, message: string, tone: string) => void,
) {
  const router = useRouter()

  const roleFormMode = ref<'create' | 'edit'>('create')
  const isSavingRole = ref(false)
  const roleFeedback = ref('')
  const roleFeedbackTone = ref('accent')
  const roleValidationAttempted = ref(false)
  const selectedRoleId = ref<string | null>(null)

  const roleForm = reactive<RolePayload>({
    codigo: '',
    nombre: '',
    descripcion: '',
    estado: true,
    permission_ids: [],
    user_ids: [],
  })

  const roleFormErrors = computed<Record<RoleFieldKey, string>>(() => ({
    codigo: roleForm.codigo.trim() ? '' : 'Ingresa el codigo del rol.',
    nombre: roleForm.nombre.trim() ? '' : 'Ingresa el nombre del rol.',
  }))

  function hasRoleFormErrors(): boolean {
    return Object.values(roleFormErrors.value).some(Boolean)
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

  function syncFormWithRole(role: AccessRole): void {
    roleForm.codigo = role.codigo
    roleForm.nombre = role.nombre
    roleForm.descripcion = role.descripcion
    roleForm.estado = role.estado
    roleForm.permission_ids = [...role.permission_ids]
    roleForm.user_ids = [...role.user_ids]
  }

  function startCreateRole(): void {
    selectedRoleId.value = null
    roleFormMode.value = 'create'
    roleFeedback.value = ''
    roleFeedbackTone.value = 'accent'
    resetRoleForm()
  }

  function selectRole(role: AccessRole): void {
    selectedRoleId.value = role.id
    roleFormMode.value = 'edit'
    roleFeedback.value = ''
    roleFeedbackTone.value = 'accent'
    roleValidationAttempted.value = false
    syncFormWithRole(role)
  }

  async function saveRole(): Promise<void> {
    isSavingRole.value = true
    roleFeedback.value = ''
    roleValidationAttempted.value = true

    if (hasRoleFormErrors()) {
      roleFeedbackTone.value = 'warning'
      roleFeedback.value = 'Completa codigo y nombre antes de guardar el rol.'
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
      pushToast(
        roleFormMode.value === 'create' ? 'Rol creado' : 'Rol actualizado',
        result.message,
        'success',
      )
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

  return {
    roleFormMode,
    isSavingRole,
    roleFeedback,
    roleFeedbackTone,
    roleValidationAttempted,
    selectedRoleId,
    roleForm,
    roleFormErrors,
    hasRoleFormErrors,
    resetRoleForm,
    syncFormWithRole,
    startCreateRole,
    selectRole,
    saveRole,
  }
}
