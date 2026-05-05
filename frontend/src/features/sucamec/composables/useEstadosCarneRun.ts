import { computed, ref } from 'vue'

import {
  buildEstadosCarneDownloadUrl,
  cancelEstadosCarneRun,
  getEstadosCarneRun,
  startEstadosCarneRun,
  uploadEstadosCarneInput,
  type EstadosCarneInputPreviewRow,
  type EstadosCarneInputValidation,
  type EstadosCarneJob,
} from '@/features/sucamec/api/estadosCarne.api'

type FeedbackTone = 'success' | 'warning' | 'danger' | 'accent'
type SucamecGroup = 'JV' | 'SELVA' | 'TODOS'

const ACTIVE_JOB_STORAGE_KEY = 'sigemo-sucamec-estados-active-job-id'

const selectedInputFile = ref<File | null>(null)
const uploadedFilename = ref('')
const inputValidation = ref<EstadosCarneInputValidation | null>(null)
const inputPreview = ref<EstadosCarneInputPreviewRow[]>([])
const sucamecGroup = ref<SucamecGroup>('JV')
const estadosJob = ref<EstadosCarneJob | null>(null)
const estadosFeedback = ref('')
const estadosFeedbackTone = ref<FeedbackTone>('accent')
const isUploadingInput = ref(false)
const isStartingRun = ref(false)
const isCancellingRun = ref(false)
const isInitialized = ref(false)
const isGlobalRunAlertVisible = ref(false)
let jobPollingId: number | null = null
let terminalAlertTimerId: number | null = null

const isRunningEstadosJob = computed(() =>
  estadosJob.value?.status === 'queued' || estadosJob.value?.status === 'running',
)

const estadosStatusLabel = computed(() => {
  if (!estadosJob.value) return 'Listo'
  if (estadosJob.value.status === 'success') return 'Finalizado'
  if (estadosJob.value.status === 'error') return 'Error'
  if (estadosJob.value.status === 'cancelled') return 'Cancelado'
  if (estadosJob.value.status === 'running') return 'Ejecutando'
  return 'Pendiente'
})

const estadosDownloadUrl = computed(() =>
  estadosJob.value?.has_result ? buildEstadosCarneDownloadUrl(estadosJob.value.id) : '',
)

const canStartEstadosFlow = computed(() =>
  Boolean(uploadedFilename.value && inputValidation.value?.is_valid && !isStartingRun.value && !isRunningEstadosJob.value),
)

const globalRunTone = computed<FeedbackTone>(() => {
  if (!estadosJob.value) return 'accent'
  if (estadosJob.value.status === 'success') return 'success'
  if (estadosJob.value.status === 'error') return 'danger'
  if (estadosJob.value.status === 'cancelled') return 'warning'
  return 'accent'
})

const globalRunMessage = computed(() => {
  if (!estadosJob.value) return ''
  return `${estadosJob.value.message || estadosStatusLabel.value}. Grupo ${estadosJob.value.grupo}. Archivo ${estadosJob.value.input_filename}.`
})

const globalRunAlertVisible = computed(() => Boolean(estadosJob.value && isGlobalRunAlertVisible.value))

const isTerminalEstadosJob = computed(() => Boolean(estadosJob.value && isTerminalStatus(estadosJob.value)))

function isTerminalStatus(job: EstadosCarneJob): boolean {
  return job.status === 'success' || job.status === 'error' || job.status === 'cancelled'
}

function persistActiveJob(job: EstadosCarneJob | null): void {
  if (job && !isTerminalStatus(job)) {
    localStorage.setItem(ACTIVE_JOB_STORAGE_KEY, job.id)
    return
  }

  localStorage.removeItem(ACTIVE_JOB_STORAGE_KEY)
}

function clearTerminalAlertTimer(): void {
  if (terminalAlertTimerId !== null) {
    window.clearTimeout(terminalAlertTimerId)
    terminalAlertTimerId = null
  }
}

function showGlobalRunAlert(job: EstadosCarneJob): void {
  isGlobalRunAlertVisible.value = true
  clearTerminalAlertTimer()

  if (isTerminalStatus(job)) {
    terminalAlertTimerId = window.setTimeout(() => {
      isGlobalRunAlertVisible.value = false
      terminalAlertTimerId = null
    }, 8000)
  }
}

function stopJobPolling(): void {
  if (jobPollingId !== null) {
    window.clearInterval(jobPollingId)
    jobPollingId = null
  }
}

async function refreshEstadosJob(jobId: string): Promise<void> {
  const response = await getEstadosCarneRun(jobId)
  estadosJob.value = response.job
  persistActiveJob(response.job)
  showGlobalRunAlert(response.job)

  if (isTerminalStatus(response.job)) {
    stopJobPolling()
  }
}

function startJobPolling(jobId: string): void {
  stopJobPolling()
  jobPollingId = window.setInterval(() => {
    void refreshEstadosJob(jobId)
  }, 3000)
}

async function initializeEstadosRunState(): Promise<void> {
  if (isInitialized.value) return
  isInitialized.value = true

  const storedJobId = localStorage.getItem(ACTIVE_JOB_STORAGE_KEY)
  if (!storedJobId) return

  try {
    await refreshEstadosJob(storedJobId)
    if (estadosJob.value && !isTerminalStatus(estadosJob.value)) {
      showGlobalRunAlert(estadosJob.value)
      startJobPolling(estadosJob.value.id)
    }
  } catch {
    localStorage.removeItem(ACTIVE_JOB_STORAGE_KEY)
  }
}

function handleInputFileChange(file: File | null): void {
  selectedInputFile.value = file
  uploadedFilename.value = ''
  inputValidation.value = null
  inputPreview.value = []
  if (!isRunningEstadosJob.value) {
    estadosJob.value = null
    estadosFeedback.value = ''
  }
}

async function uploadInputFile(): Promise<void> {
  if (!selectedInputFile.value) {
    estadosFeedbackTone.value = 'warning'
    estadosFeedback.value = 'Selecciona un archivo .xlsx antes de cargar.'
    return
  }

  isUploadingInput.value = true
  estadosFeedback.value = ''

  try {
    const response = await uploadEstadosCarneInput(selectedInputFile.value)
    uploadedFilename.value = response.filename
    inputValidation.value = response.validation
    inputPreview.value = response.preview
    estadosFeedbackTone.value = 'success'
    estadosFeedback.value = `${response.message}. ${response.validation.total_records} registros listos para procesar.`
  } catch (error) {
    uploadedFilename.value = ''
    inputValidation.value = null
    inputPreview.value = []
    estadosFeedbackTone.value = 'danger'
    estadosFeedback.value = error instanceof Error ? error.message : 'No se pudo cargar el archivo.'
  } finally {
    isUploadingInput.value = false
  }
}

async function startEstadosFlow(): Promise<void> {
  if (!uploadedFilename.value) {
    estadosFeedbackTone.value = 'warning'
    estadosFeedback.value = 'Carga el Excel antes de ejecutar la consulta.'
    return
  }

  isStartingRun.value = true
  estadosFeedback.value = ''

  try {
    const response = await startEstadosCarneRun(sucamecGroup.value, uploadedFilename.value)
    estadosJob.value = response.job
    estadosFeedbackTone.value = 'accent'
    estadosFeedback.value = response.message
    persistActiveJob(response.job)
    showGlobalRunAlert(response.job)
    startJobPolling(response.job.id)
  } catch (error) {
    estadosFeedbackTone.value = 'danger'
    estadosFeedback.value = error instanceof Error ? error.message : 'No se pudo iniciar el flujo.'
  } finally {
    isStartingRun.value = false
  }
}

async function cancelEstadosFlow(): Promise<void> {
  if (!estadosJob.value || !isRunningEstadosJob.value) return

  isCancellingRun.value = true
  estadosFeedback.value = ''

  try {
    const response = await cancelEstadosCarneRun(estadosJob.value.id)
    estadosJob.value = response.job
    estadosFeedbackTone.value = 'warning'
    estadosFeedback.value = response.message
    persistActiveJob(response.job)
    showGlobalRunAlert(response.job)
    stopJobPolling()
  } catch (error) {
    estadosFeedbackTone.value = 'danger'
    estadosFeedback.value = error instanceof Error ? error.message : 'No se pudo cancelar la ejecucion.'
  } finally {
    isCancellingRun.value = false
  }
}

export function useEstadosCarneRun() {
  return {
    canStartEstadosFlow,
    cancelEstadosFlow,
    estadosDownloadUrl,
    estadosFeedback,
    estadosFeedbackTone,
    estadosJob,
    estadosStatusLabel,
    globalRunAlertVisible,
    globalRunMessage,
    globalRunTone,
    handleInputFileChange,
    initializeEstadosRunState,
    inputPreview,
    inputValidation,
    isCancellingRun,
    isTerminalEstadosJob,
    isRunningEstadosJob,
    isStartingRun,
    isUploadingInput,
    selectedInputFile,
    startEstadosFlow,
    stopJobPolling,
    sucamecGroup,
    uploadInputFile,
    uploadedFilename,
  }
}
