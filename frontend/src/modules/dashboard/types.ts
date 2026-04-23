export type TrackingStatus = 'Vigente' | 'Por vencer' | 'Vencido'

export interface TrackingRow {
  id: string
  documentNumber: string
  fullName: string
  unit: string
  position: string
  status: TrackingStatus
  daysRemaining: number
}

export interface TrackingFilters {
  documentNumber: string
  status: 'Todos' | TrackingStatus
  unit: string
  recruiter: string
}
