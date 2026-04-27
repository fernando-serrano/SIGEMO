import type { TrackingRow } from '../types'

export const mockTrackingRows: TrackingRow[] = [
  {
    id: '1',
    documentNumber: '45829301',
    fullName: 'RICARDO SANCHEZ PERALTA',
    unit: 'UNIDAD T-CYBER',
    position: 'Operador Senior',
    status: 'Vigente',
    daysRemaining: 2,
  },
  {
    id: '2',
    documentNumber: '72019483',
    fullName: 'ELENA VASQUEZ RIOS',
    unit: 'UNIDAD NORTH-HUB',
    position: 'Analista de Sistemas',
    status: 'Por vencer',
    daysRemaining: 5,
  },
  {
    id: '3',
    documentNumber: '10493822',
    fullName: 'MARCOS TOLEDO CUEVA',
    unit: 'UNIDAD T-CYBER',
    position: 'Ingeniero Biomedico',
    status: 'Vencido',
    daysRemaining: 12,
  },
  {
    id: '4',
    documentNumber: '33948572',
    fullName: 'SOFIA LUJAN VEGA',
    unit: 'CENTRAL-CMD',
    position: 'Tecnico Operativo',
    status: 'Vigente',
    daysRemaining: 1,
  },
]
