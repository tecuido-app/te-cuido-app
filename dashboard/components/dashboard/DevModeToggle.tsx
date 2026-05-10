'use client'

import type { Status } from '@/lib/types'

type DevModeToggleProps = {
  currentStatus: Status
  onCycle: () => void
}

const statusOrder: Status[] = ['ok', 'alert', 'emergency']

export function DevModeToggle({ currentStatus, onCycle }: DevModeToggleProps) {
  const currentIndex = statusOrder.indexOf(currentStatus)
  const nextStatus = statusOrder[(currentIndex + 1) % statusOrder.length]

  return (
    <button
      onClick={onCycle}
      className="fixed bottom-6 right-6 z-50 px-4 py-2.5 rounded-xl bg-slate-800/90 border border-slate-700/50 text-slate-300 text-xs font-mono shadow-2xl backdrop-blur-sm hover:bg-slate-700/90 transition-all flex items-center gap-2"
    >
      <span className="text-cyan-400 font-semibold">DEV</span>
      <span className="text-slate-600">|</span>
      <span className="text-slate-400">
        {currentStatus} <span className="text-slate-600">→</span> {nextStatus}
      </span>
    </button>
  )
}
