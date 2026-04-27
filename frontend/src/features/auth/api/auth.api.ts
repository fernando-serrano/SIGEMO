import type { LoginApiResponse, LoginPayload, LoginUser } from '../types'

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.trim()

function buildLoginUrl(): string {
  if (!API_BASE_URL) {
    return '/api/login'
  }

  return `${API_BASE_URL.replace(/\/$/, '')}/api/login`
}

export async function login(payload: LoginPayload): Promise<LoginUser> {
  const response = await fetch(buildLoginUrl(), {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  })

  const contentType = response.headers.get('content-type') || ''

  if (!contentType.includes('application/json')) {
    throw new Error('El servidor no devolvio una respuesta JSON valida')
  }

  const result = (await response.json()) as LoginApiResponse

  if (!response.ok || !result.ok || !result.user) {
    throw new Error(result.message || 'No se pudo iniciar sesion')
  }

  return result.user
}
