import type {
  AccessCatalogResponse,
  MutationResponse,
  PermissionPayload,
  RolePayload,
  RolePermissionsPayload,
  UserPayload,
} from '../types'
import { apiClient } from '@/shared/api/client'

export async function fetchAccessCatalog(): Promise<AccessCatalogResponse> {
  return apiClient.get<AccessCatalogResponse>('/api/access/catalog')
}

export async function createUser(payload: UserPayload): Promise<MutationResponse> {
  return apiClient.post<MutationResponse>('/api/users', payload)
}

export async function updateUser(userId: string, payload: UserPayload): Promise<MutationResponse> {
  return apiClient.put<MutationResponse>(`/api/users/${userId}`, payload)
}

export async function updateUserStatus(userId: string, isActive: boolean): Promise<MutationResponse> {
  return apiClient.patch<MutationResponse>(`/api/users/${userId}/status`, { is_active: isActive })
}

export async function updateRolePermissions(roleId: string, payload: RolePermissionsPayload): Promise<MutationResponse> {
  return apiClient.put<MutationResponse>(`/api/roles/${roleId}/permissions`, payload)
}

export async function createRole(payload: RolePayload): Promise<MutationResponse> {
  return apiClient.post<MutationResponse>('/api/roles', payload)
}

export async function updateRole(roleId: string, payload: RolePayload): Promise<MutationResponse> {
  return apiClient.put<MutationResponse>(`/api/roles/${roleId}`, payload)
}

export async function createPermission(payload: PermissionPayload): Promise<MutationResponse> {
  return apiClient.post<MutationResponse>('/api/permissions', payload)
}

export async function updatePermission(permissionId: string, payload: PermissionPayload): Promise<MutationResponse> {
  return apiClient.put<MutationResponse>(`/api/permissions/${permissionId}`, payload)
}
