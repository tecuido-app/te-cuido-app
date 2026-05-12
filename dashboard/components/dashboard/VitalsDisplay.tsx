'use client'

import type { Vitals, Status } from '@/lib/types'

type VitalsDisplayProps = {
  vitals: Vitals
  status: Status
}

function HeartIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z" />
    </svg>
  )
}

function LungsIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10" />
      <path d="M12 6v6l4 2" />
    </svg>
  )
}

function ThermometerIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M14 4v10.54a4 4 0 1 1-4 0V4a2 2 0 0 1 4 0Z" />
    </svg>
  )
}

function formatTimeAgo(isoString: string): string {
  const now = new Date()
  const then = new Date(isoString)
  const diffMs = now.getTime() - then.getTime()
  const diffMins = Math.floor(diffMs / 60000)

  if (diffMins < 1) return 'Now'
  if (diffMins === 1) return '1 min ago'
  if (diffMins < 60) return `${diffMins} min ago`

  const diffHours = Math.floor(diffMins / 60)
  if (diffHours === 1) return '1h ago'
  return `${diffHours}h ago`
}

function isVitalCritical(type: 'heartRate' | 'spo2' | 'skinTemp', value: number): boolean {
  if (type === 'heartRate') return value < 50 || value > 120
  if (type === 'spo2') return value < 92
  if (type === 'skinTemp') return value < 35 || value > 38
  return false
}

export function VitalsDisplay({ vitals, status }: VitalsDisplayProps) {
  const vitalItems = [
    {
      key: 'heartRate' as const,
      icon: HeartIcon,
      label: 'HR',
      value: vitals.heartRate,
      unit: 'bpm',
    },
    {
      key: 'spo2' as const,
      icon: LungsIcon,
      label: 'SpO2',
      value: vitals.spo2,
      unit: '%',
    },
    {
      key: 'skinTemp' as const,
      icon: ThermometerIcon,
      label: 'Temp',
      value: vitals.skinTemp.toFixed(1),
      unit: '°',
    },
  ]

  return (
    <section className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-sm lg:text-base font-semibold text-slate-400 uppercase tracking-wider">
          Vital signs
        </h2>
        <span className="text-xs lg:text-sm text-slate-600">
          {formatTimeAgo(vitals.timestamp)}
        </span>
      </div>

      <div className="grid grid-cols-3 gap-3 lg:gap-4">
        {vitalItems.map(({ key, icon: Icon, label, value, unit }) => {
          const isCritical = isVitalCritical(key, typeof value === 'string' ? parseFloat(value) : value)
          const showWarning = status !== 'ok' && isCritical

          return (
            <div
              key={key}
              className={`relative overflow-hidden rounded-2xl p-4 lg:p-6 text-center transition-all duration-300 ${
                showWarning
                  ? 'bg-rose-500/10 border border-rose-500/30 shadow-lg shadow-rose-500/10'
                  : 'bg-slate-800/50 border border-slate-700/50 hover:border-slate-600/50'
              }`}
            >
              {showWarning && (
                <div className="absolute inset-0 bg-gradient-to-br from-rose-500/5 to-transparent" />
              )}

              <div className="relative">
                <Icon
                  className={`w-5 h-5 lg:w-6 lg:h-6 mx-auto mb-3 ${
                    showWarning ? 'text-rose-400' : 'text-cyan-400'
                  }`}
                />
                <div className={`text-3xl lg:text-5xl font-bold tracking-tight mb-1 ${
                  showWarning ? 'text-rose-400' : 'text-white'
                }`}>
                  {value}
                  <span className="text-lg lg:text-2xl font-normal text-slate-500 ml-0.5">
                    {unit}
                  </span>
                </div>
                <div className="text-xs lg:text-sm text-slate-500 font-medium">
                  {label}
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </section>
  )
}
