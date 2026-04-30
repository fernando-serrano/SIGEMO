import type { LoginApiResponse, LoginPayload, LoginUser } from '../types'
import { apiClient } from '@/shared/api/client'

export async function login(payload: LoginPayload): Promise<LoginUser> {
  try {
    const result = await apiClient.post<LoginApiResponse>('/api/login', payload, {
      maxRetries: 1,
      retryDelayMs: 350,
    })

    if (!result.ok || !result.user) {
      throw new Error(result.message || 'No se pudo iniciar sesion')
    }

    return result.user
  } catch (error) {
    if (error instanceof Error) {
      throw error
    }
    throw new Error('No se pudo iniciar sesion')
  }
}
