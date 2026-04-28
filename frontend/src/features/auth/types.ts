export type ThemeName = 'dark' | 'light' | 'corp' | 'corp-dark'

export interface LoginPayload {
  username: string
  password_hash: string
}

export interface LoginUser {
  username: string
  name?: string
  last_name?: string
  fullname?: string
  email?: string
  area?: string
  rol_id?: string | number | null
  role?: string
  role_name?: string
}

export interface LoginApiResponse {
  ok: boolean
  message?: string
  user?: LoginUser
}
