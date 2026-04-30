import { ref } from 'vue'
import type { AccessPermission, AccessRole, AccessUser } from '../types'
import { fetchAccessCatalog } from '../api/users.api'

export function useUsersCatalog() {
  const isLoading = ref(true)
  const loadError = ref('')

  const catalog = ref<{
    users: AccessUser[]
    roles: AccessRole[]
    permissions: AccessPermission[]
  }>({
    users: [],
    roles: [],
    permissions: [],
  })

  async function loadModuleData(): Promise<void> {
    isLoading.value = true
    loadError.value = ''

    try {
      const response = await fetchAccessCatalog()
      catalog.value = {
        users: response.users,
        roles: response.roles,
        permissions: response.permissions,
      }
    } catch (error) {
      loadError.value = error instanceof Error ? error.message : 'No se pudo cargar el modulo de usuarios'
    } finally {
      isLoading.value = false
    }
  }

  return {
    isLoading,
    loadError,
    catalog,
    loadModuleData,
  }
}
