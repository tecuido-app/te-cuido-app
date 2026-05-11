'use client'

import type { EventType } from '@/lib/types'

type EmergencyBannerProps = {
  eventType: EventType
}

const eventTypeLabels: Record<EventType, string> = {
  Fall: 'Possible fall detected',
  LowHR: 'Low heart rate',
  LowSpO2: 'Low blood oxygen',
}

function PhoneIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z" />
    </svg>
  )
}

export function EmergencyBanner({ eventType }: EmergencyBannerProps) {
  return (
    <section className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-rose-900/50 to-slate-900/80 border border-rose-500/50 backdrop-blur-xl">
      {/* Animated pulse background */}
      <div className="absolute inset-0 bg-rose-500/20 animate-pulse" />
      
      {/* Radial glow */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,_var(--tw-gradient-stops))] from-rose-500/30 via-transparent to-transparent" />
      
      <div className="relative p-8 lg:p-12 text-center">
        <div className="w-16 h-16 lg:w-24 lg:h-24 rounded-full bg-gradient-to-br from-rose-500 to-rose-600 flex items-center justify-center mx-auto mb-5 lg:mb-6 shadow-2xl shadow-rose-500/40 animate-pulse">
          <PhoneIcon className="w-8 h-8 lg:w-12 lg:h-12 text-white" />
        </div>
        
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-rose-500/20 border border-rose-500/40 mb-4">
          <span className="w-2 h-2 rounded-full bg-rose-400 animate-pulse" />
          <span className="text-rose-300 text-xs lg:text-sm font-semibold uppercase tracking-wider">
            Active emergency
          </span>
        </div>
        
        <h2 className="text-white font-bold text-2xl lg:text-4xl mb-3 tracking-tight">
          {eventTypeLabels[eventType]}
        </h2>
        <p className="text-rose-200/80 text-base lg:text-xl">
          Contacting support network
        </p>
      </div>
    </section>
  )
}
