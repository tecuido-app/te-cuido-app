export type Status = 'ok' | 'alert' | 'emergency'

export type Vitals = {
  heartRate: number          // BPM
  spo2: number               // %
  skinTemp: number           // °C
  timestamp: string          // ISO
}

export type EventType = 'Fall' | 'LowHR' | 'LowSpO2'

export type ActionType =
  | 'GracePeriod'
  | 'AIDismissed'
  | 'NotifiedContact'
  | 'Escalated'
  | 'WellbeingConfirmed'
  | 'Resolved'

export type AgentAction = {
  type: ActionType
  contactIndex?: number      // 0, 1, 2 — qué contacto fue notificado
  timestamp: string
  txHash: string             // hash de la tx en Solana, para link a Explorer
  note?: string
}

export type EventLog = {
  id: string
  type: EventType
  severity: 1 | 2 | 3
  value: number              // ej: 38 BPM, 87 SpO2, 600 segundos sin movimiento
  timestamp: string
  actions: AgentAction[]
  resolved: boolean
  resolvedAt?: string
}

export type DashboardData = {
  patientName: string
  patientAge: number
  status: Status
  vitals: Vitals
  activeEvent: EventLog | null
  history: EventLog[]
  graceSecondsRemaining?: number   // solo si status === 'alert'
}
