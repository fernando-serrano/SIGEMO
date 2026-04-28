export interface AccessPermission {
  id: string
  codigo: string
  nombre: string
  modulo: string
  accion: string
  descripcion: string
  estado: boolean
}

export interface AccessRole {
  id: string
  codigo: string
  nombre: string
  descripcion: string
  estado: boolean
  permission_ids: string[]
}

export interface AccessUser {
  id: string
  username: string
  name: string
  last_name: string
  fullname: string
  email: string
  area: string
  is_active: boolean
  role_ids: string[]
  permission_ids: string[]
  effective_permission_ids: string[]
}

export interface AccessCatalogResponse {
  ok: boolean
  users: AccessUser[]
  roles: AccessRole[]
  permissions: AccessPermission[]
}

export interface UserPayload {
  username: string
  password_hash?: string
  name: string
  last_name: string
  email: string
  area: string
  is_active: boolean
  role_ids: string[]
  permission_ids: string[]
}

export interface UserAccessPayload {
  role_ids: string[]
  permission_ids: string[]
}

export interface RolePermissionsPayload {
  permission_ids: string[]
}

export interface MutationResponse {
  ok: boolean
  message: string
  user?: AccessUser
  role?: AccessRole
}
