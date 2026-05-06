export const SESSION_USER_KEY = 'sigemo-user'
export const SESSION_TOKEN_KEY = 'sigemo-token'

export interface AppSessionUser {
  id?: string
  username?: string
  name?: string
  last_name?: string
  fullname?: string
  email?: string
  area?: string
  rol_id?: string | number | null
  role?: string
  role_name?: string
}

export function getAccessToken(): string {
  return sessionStorage.getItem(SESSION_TOKEN_KEY) ?? ''
}

export function saveAccessToken(token: string): void {
  sessionStorage.setItem(SESSION_TOKEN_KEY, token)
}

export function saveSessionUser(user: AppSessionUser): void {
  sessionStorage.setItem(SESSION_USER_KEY, JSON.stringify(user))
}

export function readSessionUser<T extends AppSessionUser = AppSessionUser>(): T | null {
  const rawSession = sessionStorage.getItem(SESSION_USER_KEY)
  if (!rawSession) return null

  try {
    return JSON.parse(rawSession) as T
  } catch {
    clearSession()
    return null
  }
}

export function hasActiveSession(): boolean {
  const user = readSessionUser()
  return Boolean((user?.id || user?.username) && getAccessToken())
}

export function clearSession(): void {
  sessionStorage.removeItem(SESSION_USER_KEY)
  sessionStorage.removeItem(SESSION_TOKEN_KEY)
}
