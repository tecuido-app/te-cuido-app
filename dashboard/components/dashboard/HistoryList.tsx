'use client'

import type { EventLog, EventType } from '@/lib/types'

type HistoryListProps = {
  events: EventLog[]
}

const eventTypeLabels: Record<EventType, string> = {
  Fall: 'Posible caida',
  LowHR: 'FC baja',
  LowSpO2: 'SpO2 bajo',
}

function formatDate(isoString: string): string {
  const date = new Date(isoString)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))

  if (diffDays === 0) return 'Hoy'
  if (diffDays === 1) return 'Ayer'
  if (diffDays < 7) return `${diffDays}d`

  return date.toLocaleDateString('es-AR', {
    day: 'numeric',
    month: 'short',
  })
}

function getResolutionText(event: EventLog): string {
  const confirmedAction = event.actions.find(
    (a) => a.type === 'WellbeingConfirmed'
  )
  if (confirmedAction?.note) {
    return confirmedAction.note
  }
  return 'Resuelto'
}

function CheckCircleIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
      <polyline points="22 4 12 14.01 9 11.01" />
    </svg>
  )
}

export function HistoryList({ events }: HistoryListProps) {
  if (events.length === 0) {
    return (
      <section className="space-y-3">
        <h2 className="text-sm lg:text-base font-semibold text-slate-400 uppercase tracking-wider">
          Historial
        </h2>
        <div className="rounded-2xl bg-slate-800/30 border border-slate-700/30 p-6 lg:p-8 text-center">
          <p className="text-slate-600 text-sm lg:text-base">
            Sin eventos previos
          </p>
        </div>
      </section>
    )
  }

  return (
    <section className="space-y-3">
      <h2 className="text-sm lg:text-base font-semibold text-slate-400 uppercase tracking-wider">
        Historial
      </h2>
      
      <div className="rounded-2xl overflow-hidden bg-slate-800/30 border border-slate-700/30">
        {events.map((event, index) => (
          <div
            key={event.id}
            className={`flex items-center gap-3 lg:gap-4 px-4 lg:px-5 py-3.5 lg:py-4 ${
              index !== events.length - 1 ? 'border-b border-slate-700/30' : ''
            }`}
          >
            <div className="w-9 h-9 lg:w-10 lg:h-10 rounded-xl bg-cyan-500/10 flex items-center justify-center shrink-0">
              <CheckCircleIcon className="w-4 h-4 lg:w-5 lg:h-5 text-cyan-400" />
            </div>
            
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <span className="font-medium text-white text-sm lg:text-base">
                  {eventTypeLabels[event.type]}
                </span>
                <span className="text-cyan-400 text-xs lg:text-sm">
                  Resuelto
                </span>
              </div>
              <p className="text-xs lg:text-sm text-slate-500 truncate">
                {getResolutionText(event)}
              </p>
            </div>
            
            <span className="text-xs lg:text-sm text-slate-600 shrink-0">
              {formatDate(event.timestamp)}
            </span>
          </div>
        ))}
      </div>
    </section>
  )
}
