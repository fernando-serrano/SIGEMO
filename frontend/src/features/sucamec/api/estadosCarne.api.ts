const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.trim() ?? ''

export type EstadosCarneJobStatus = 'queued' | 'running' | 'success' | 'error' | 'cancelled'

export interface EstadosCarneJob {
  id: string
  grupo: string
  input_filename: string
  display_input_filename: string
  status: EstadosCarneJobStatus
  message: string
  created_at: string
  started_at: string | null
  finished_at: string | null
  return_code: number | null
  has_result: boolean
  result_files: string[]
  log_tail: string
}

export interface EstadosCarneInputPreviewRow {
  row_number: number
  nro_documento: string
}

export interface EstadosCarneInputValidation {
  is_valid: boolean
  required_columns: string[]
  detected_columns: string[]
  document_column: string
  total_records: number
  omitted_rows: number[]
  omitted_rows_count: number
}

export interface UploadResponse {
  ok: boolean
  message: string
  filename: string
  size_bytes: number
  validation: EstadosCarneInputValidation
  preview: EstadosCarneInputPreviewRow[]
}

interface RunResponse {
  ok: boolean
  message: string
  job: EstadosCarneJob
}

interface JobResponse {
  ok: boolean
  job: EstadosCarneJob
}

interface CancelResponse {
  ok: boolean
  message: string
  job: EstadosCarneJob
}

function buildApiUrl(path: string): string {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`
  return API_BASE_URL ? `${API_BASE_URL.replace(/\/$/, '')}${normalizedPath}` : normalizedPath
}

async function parseJsonResponse<T>(response: Response): Promise<T> {
  const data = await response.json()

  if (!response.ok || data?.ok === false) {
    throw new Error(data?.message || 'No se pudo completar la solicitud')
  }

  return data as T
}

export async function uploadEstadosCarneInput(file: File): Promise<UploadResponse> {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(buildApiUrl('/api/sucamec/estados-carne/upload'), {
    method: 'POST',
    body: formData,
  })

  return parseJsonResponse<UploadResponse>(response)
}

export async function startEstadosCarneRun(grupo: string, inputFilename: string): Promise<RunResponse> {
  const formData = new FormData()
  formData.append('grupo', grupo)
  formData.append('input_filename', inputFilename)

  const response = await fetch(buildApiUrl('/api/sucamec/estados-carne/runs'), {
    method: 'POST',
    body: formData,
  })

  return parseJsonResponse<RunResponse>(response)
}

export async function getEstadosCarneRun(jobId: string): Promise<JobResponse> {
  const response = await fetch(buildApiUrl(`/api/sucamec/estados-carne/runs/${jobId}`))
  return parseJsonResponse<JobResponse>(response)
}

export async function cancelEstadosCarneRun(jobId: string): Promise<CancelResponse> {
  const response = await fetch(buildApiUrl(`/api/sucamec/estados-carne/runs/${jobId}/cancel`), {
    method: 'POST',
  })

  return parseJsonResponse<CancelResponse>(response)
}

export function buildEstadosCarneDownloadUrl(jobId: string): string {
  return buildApiUrl(`/api/sucamec/estados-carne/runs/${jobId}/download`)
}
