import { apiClient } from '@/shared/api/client'
import { getAccessToken } from '@/shared/session/session'

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

export async function uploadEstadosCarneInput(file: File): Promise<UploadResponse> {
  const formData = new FormData()
  formData.append('file', file)

  return apiClient.postForm<UploadResponse>('/api/sucamec/estados-carne/upload', formData)
}

export async function startEstadosCarneRun(grupo: string, inputFilename: string): Promise<RunResponse> {
  const formData = new FormData()
  formData.append('grupo', grupo)
  formData.append('input_filename', inputFilename)

  return apiClient.postForm<RunResponse>('/api/sucamec/estados-carne/runs', formData)
}

export async function getEstadosCarneRun(jobId: string): Promise<JobResponse> {
  return apiClient.get<JobResponse>(`/api/sucamec/estados-carne/runs/${jobId}`)
}

export async function cancelEstadosCarneRun(jobId: string): Promise<CancelResponse> {
  return apiClient.post<CancelResponse>(`/api/sucamec/estados-carne/runs/${jobId}/cancel`)
}

export function buildEstadosCarneDownloadUrl(jobId: string): string {
  const token = getAccessToken()
  const tokenQuery = token ? `?access_token=${encodeURIComponent(token)}` : ''
  return apiClient.buildUrl(`/api/sucamec/estados-carne/runs/${jobId}/download${tokenQuery}`)
}
