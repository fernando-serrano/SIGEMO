import type { LoginApiResponse, LoginPayload, LoginUser } from '../types'

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.trim()
const RETRYABLE_HTTP_STATUS = new Set([502, 503, 504])

function buildLoginUrl(): string {
  if (!API_BASE_URL) {
    return '/api/login'
  }

  return `${API_BASE_URL.replace(/\/$/, '')}/api/login`
}

function wait(ms: number): Promise<void> {
  return new Promise((resolve) => {
    window.setTimeout(resolve, ms)
  })
}

async function sendLoginRequest(payload: LoginPayload): Promise<Response> {
  return fetch(buildLoginUrl(), {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  })
}

async function readLoginResponse(response: Response): Promise<LoginApiResponse> {
  const contentType = response.headers.get('content-type') || ''
  const rawBody = await response.text()

  if (!rawBody.trim()) {
    throw new Error('El servidor devolvio una respuesta vacia')
  }

  if (!contentType.includes('application/json')) {
    throw new Error('El backend respondio con un formato inesperado antes de completar el inicio de sesion')
  }

  try {
    return JSON.parse(rawBody) as LoginApiResponse
  } catch {
    throw new Error('El backend devolvio un JSON invalido durante el inicio de sesion')
  }
}

function shouldRetry(response: Response | null, error: unknown): boolean {
  if (response && (RETRYABLE_HTTP_STATUS.has(response.status) || !response.headers.get('content-type')?.includes('application/json'))) {
    return true
  }

  return error instanceof TypeError
}

export async function login(payload: LoginPayload): Promise<LoginUser> {
  let lastError: unknown = null

  for (let attempt = 1; attempt <= 2; attempt += 1) {
    let response: Response | null = null

    try {
      response = await sendLoginRequest(payload)
      const result = await readLoginResponse(response)

      if (!response.ok || !result.ok || !result.user) {
        throw new Error(result.message || 'No se pudo iniciar sesion')
      }

      return result.user
    } catch (error) {
      lastError = error

      if (attempt < 2 && shouldRetry(response, error)) {
        await wait(350)
        continue
      }

      throw error
    }
  }

  throw lastError instanceof Error ? lastError : new Error('No se pudo iniciar sesion')
}
