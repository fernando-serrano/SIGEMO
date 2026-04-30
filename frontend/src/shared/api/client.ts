const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.trim()

export interface ApiClientOptions extends RequestInit {
  retryableStatuses?: number[]
  maxRetries?: number
  retryDelayMs?: number
}

export class ApiClient {
  private baseUrl: string

  constructor(baseUrl?: string) {
    this.baseUrl = baseUrl || ''
  }

  private buildUrl(path: string): string {
    const normalizedPath = path.startsWith('/') ? path : `/${path}`
    
    if (!this.baseUrl) {
      return normalizedPath
    }

    return `${this.baseUrl.replace(/\/$/, '')}${normalizedPath}`
  }

  async get<T>(path: string, options?: ApiClientOptions): Promise<T> {
    return this.request<T>(path, { ...options, method: 'GET' })
  }

  async post<T>(path: string, body?: unknown, options?: ApiClientOptions): Promise<T> {
    return this.request<T>(path, { 
      ...options, 
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    })
  }

  async put<T>(path: string, body?: unknown, options?: ApiClientOptions): Promise<T> {
    return this.request<T>(path, { 
      ...options, 
      method: 'PUT',
      body: body ? JSON.stringify(body) : undefined,
    })
  }

  async patch<T>(path: string, body?: unknown, options?: ApiClientOptions): Promise<T> {
    return this.request<T>(path, { 
      ...options, 
      method: 'PATCH',
      body: body ? JSON.stringify(body) : undefined,
    })
  }

  async delete<T>(path: string, options?: ApiClientOptions): Promise<T> {
    return this.request<T>(path, { ...options, method: 'DELETE' })
  }

  private async request<T>(path: string, options?: ApiClientOptions): Promise<T> {
    const url = this.buildUrl(path)
    const maxRetries = options?.maxRetries ?? 0
    const retryDelayMs = options?.retryDelayMs ?? 350
    const retryableStatuses = new Set(options?.retryableStatuses ?? [502, 503, 504])

    let lastError: unknown = null

    for (let attempt = 1; attempt <= maxRetries + 1; attempt++) {
      try {
        const response = await this.fetchWithDefaults(url, options)
        const result = await this.parseResponse<T>(response)
        return result
      } catch (error) {
        lastError = error

        if (attempt <= maxRetries && this.shouldRetry(error)) {
          await this.wait(retryDelayMs)
          continue
        }

        throw error
      }
    }

    throw lastError instanceof Error ? lastError : new Error('Request failed')
  }

  private async fetchWithDefaults(url: string, options?: ApiClientOptions): Promise<Response> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options?.headers as Record<string, string> || {}),
    }

    return fetch(url, {
      ...options,
      headers,
    })
  }

  private async parseResponse<T>(response: Response): Promise<T> {
    const contentType = response.headers.get('content-type') || ''

    if (!contentType.includes('application/json')) {
      throw new Error('El servidor no devolvió una respuesta JSON válida')
    }

    const text = await response.text()
    
    if (!text.trim()) {
      throw new Error('El servidor devolvió una respuesta vacía')
    }

    try {
      const data = JSON.parse(text) as T
      
      if (!response.ok && (data as any).ok === false) {
        throw new Error((data as any).message || 'Error en la solicitud')
      }

      return data
    } catch (error) {
      if (error instanceof Error) {
        throw error
      }
      throw new Error('El servidor devolvió un JSON inválido')
    }
  }

  private shouldRetry(error: unknown): boolean {
    return error instanceof TypeError
  }

  private wait(ms: number): Promise<void> {
    return new Promise((resolve) => window.setTimeout(resolve, ms))
  }
}

export const apiClient = new ApiClient(API_BASE_URL)
