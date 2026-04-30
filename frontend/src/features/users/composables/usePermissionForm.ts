import { computed, reactive, ref, type Ref } from 'vue'
import { useRouter } from 'vue-router'
import type { AccessPermission, PermissionPayload } from '../types'
import { createPermission, updatePermission } from '../api/users.api'

export type PermissionFieldKey = 'codigo' | 'nombre' | 'modulo' | 'accion'

export function usePermissionForm(
  catalogPermissions: Ref<AccessPermission[]>,
  loadModuleData: () => Promise<void>,
  pushToast: (title: string, message: string, tone: string) => void,
) {
  const router = useRouter()

  const permissionFormMode = ref<'create' | 'edit'>('create')
  const isSavingPermission = ref(false)
  const permissionFeedback = ref('')
  const permissionFeedbackTone = ref('accent')
  const permissionValidationAttempted = ref(false)
  const selectedPermissionId = ref<string | null>(null)

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

  const permissionFormErrors = computed<Record<PermissionFieldKey, string>>(() => ({
    codigo: permissionForm.codigo.trim() ? '' : 'Ingresa el codigo del permiso.',
    nombre: permissionForm.nombre.trim() ? '' : 'Ingresa el nombre del permiso.',
    modulo: permissionForm.modulo.trim() ? '' : 'Ingresa el modulo asociado.',
    accion: permissionForm.accion.trim() ? '' : 'Ingresa la accion del permiso.',
  }))

  function hasPermissionFormErrors(): boolean {
    return Object.values(permissionFormErrors.value).some(Boolean)
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

  function startCreatePermission(): void {
    selectedPermissionId.value = null
    permissionFormMode.value = 'create'
    permissionFeedback.value = ''
    permissionFeedbackTone.value = 'accent'
    resetPermissionForm()
  }

  function selectPermission(permission: AccessPermission): void {
    selectedPermissionId.value = permission.id
    permissionFormMode.value = 'edit'
    permissionFeedback.value = ''
    permissionFeedbackTone.value = 'accent'
    permissionValidationAttempted.value = false
    syncFormWithPermission(permission)
  }

  async function savePermission(): Promise<void> {
    isSavingPermission.value = true
    permissionFeedback.value = ''
    permissionValidationAttempted.value = true

    if (hasPermissionFormErrors()) {
      permissionFeedbackTone.value = 'warning'
      permissionFeedback.value = 'Completa codigo, nombre, modulo y accion antes de guardar el permiso.'
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
      pushToast(
        permissionFormMode.value === 'create' ? 'Permiso creado' : 'Permiso actualizado',
        result.message,
        'success',
      )
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

  return {
    permissionFormMode,
    isSavingPermission,
    permissionFeedback,
    permissionFeedbackTone,
    permissionValidationAttempted,
    selectedPermissionId,
    permissionForm,
    permissionFormErrors,
    hasPermissionFormErrors,
    resetPermissionForm,
    syncFormWithPermission,
    startCreatePermission,
    selectPermission,
    savePermission,
  }
}
