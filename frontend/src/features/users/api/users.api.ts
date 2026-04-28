import type {
  AccessCatalogResponse,
  MutationResponse,
  RolePermissionsPayload,
  UserPayload,
} from '../types'

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.trim()

function buildApiUrl(path: string): string {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`

  if (!API_BASE_URL) {
    return normalizedPath
  }

  return `${API_BASE_URL.replace(/\/$/, '')}${normalizedPath}`
}

async function readJsonResponse<T>(response: Response): Promise<T> {
  const contentType = response.headers.get('content-type') || ''

  if (!contentType.includes('application/json')) {
    throw new Error('El servidor no devolvio una respuesta JSON valida')
  }

  return (await response.json()) as T
}

export async function fetchAccessCatalog(): Promise<AccessCatalogResponse> {
  const response = await fetch(buildApiUrl('/api/access/catalog'))
  const result = await readJsonResponse<AccessCatalogResponse>(response)

  if (!response.ok || !result.ok) {
    throw new Error('No se pudo cargar el modulo de usuarios')
  }

  return result
}

export async function createUser(payload: UserPayload): Promise<MutationResponse> {
  const response = await fetch(buildApiUrl('/api/users'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  const result = await readJsonResponse<MutationResponse>(response)

  if (!response.ok || !result.ok) {
    throw new Error(result.message || 'No se pudo crear el usuario')
  }

  return result
}

export async function updateUser(userId: string, payload: UserPayload): Promise<MutationResponse> {
  const response = await fetch(buildApiUrl(`/api/users/${userId}`), {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  const result = await readJsonResponse<MutationResponse>(response)

  if (!response.ok || !result.ok) {
    throw new Error(result.message || 'No se pudo actualizar el usuario')
  }

  return result
}

export async function updateUserStatus(userId: string, isActive: boolean): Promise<MutationResponse> {
  const response = await fetch(buildApiUrl(`/api/users/${userId}/status`), {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ is_active: isActive }),
  })
  const result = await readJsonResponse<MutationResponse>(response)

  if (!response.ok || !result.ok) {
    throw new Error(result.message || 'No se pudo actualizar el estado del usuario')
  }

  return result
}

export async function updateRolePermissions(roleId: string, payload: RolePermissionsPayload): Promise<MutationResponse> {
  const response = await fetch(buildApiUrl(`/api/roles/${roleId}/permissions`), {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  const result = await readJsonResponse<MutationResponse>(response)

  if (!response.ok || !result.ok) {
    throw new Error(result.message || 'No se pudieron actualizar los permisos del rol')
  }

  return result
}
