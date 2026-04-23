export type ThemeName = 'dark' | 'light' | 'corp' | 'corp-dark'

export interface LoginPayload {
  username: string
  password: string
}

export interface LoginUser {
  username: string
  fullname?: string
  email?: string
  area?: string
  rol_id?: string | number | null
  role?: string
}

export interface LoginApiResponse {
  ok: boolean
  message?: string
  user?: LoginUser
}
