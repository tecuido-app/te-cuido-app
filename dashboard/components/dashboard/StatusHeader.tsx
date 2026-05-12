'use client'

import type { Status } from '@/lib/types'

type StatusHeaderProps = {
  patientName: string
  patientAge: number
  status: Status
}

const statusConfig = {
  ok: {
    label: 'Todo bien',
    bgColor: 'bg-cyan-500/15',
    textColor: 'text-cyan-400',
    dotColor: 'bg-cyan-400',
    borderColor: 'border-cyan-500/30',
    glowColor: 'shadow-cyan-500/20',
  },
  alert: {
    label: 'Verificando',
    bgColor: 'bg-amber-500/15',
    textColor: 'text-amber-400',
    dotColor: 'bg-amber-400',
    borderColor: 'border-amber-500/30',
    glowColor: 'shadow-amber-500/20',
  },
  emergency: {
    label: 'Emergencia',
    bgColor: 'bg-rose-500/15',
    textColor: 'text-rose-400',
    dotColor: 'bg-rose-400',
    borderColor: 'border-rose-500/30',
    glowColor: 'shadow-rose-500/20',
  },
}

export function StatusHeader({ patientName, patientAge, status }: StatusHeaderProps) {
  const config = statusConfig[status]

  return (
    <header className="flex items-center justify-between gap-4">
      <div className="min-w-0">
        <h1 className="text-2xl lg:text-5xl font-bold text-white tracking-tight truncate">
          {patientName}
        </h1>
        <p className="text-slate-500 text-sm lg:text-lg mt-1">
          {patientAge} anos
        </p>
      </div>
      <div
        className={`flex items-center gap-2.5 px-4 lg:px-5 py-2 lg:py-2.5 rounded-full border ${config.bgColor} ${config.borderColor} shadow-lg ${config.glowColor} shrink-0`}
      >
        <span
          className={`w-2.5 h-2.5 lg:w-3 lg:h-3 rounded-full ${config.dotColor} ${
            status !== 'ok' ? 'animate-pulse' : ''
          }`}
        />
        <span className={`text-sm lg:text-base font-semibold ${config.textColor}`}>
          {config.label}
        </span>
      </div>
    </header>
  )
}
