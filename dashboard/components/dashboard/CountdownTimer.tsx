'use client'

import type { EventType } from '@/lib/types'

type CountdownTimerProps = {
  seconds: number
  eventType: EventType
  eventValue: number
}

const eventTypeLabels: Record<EventType, string> = {
  Fall: 'Posible caida detectada',
  LowHR: 'Frecuencia cardiaca baja',
  LowSpO2: 'Oxigeno en sangre bajo',
}

const eventTypeDetails: Record<EventType, (value: number) => string> = {
  Fall: (value) => `Sin movimiento por ${Math.floor(value / 60)} minutos`,
  LowHR: (value) => `${value} latidos por minuto`,
  LowSpO2: (value) => `${value}% de saturacion`,
}

export function CountdownTimer({ seconds, eventType, eventValue }: CountdownTimerProps) {
  const isUrgent = seconds <= 15
  const isCritical = seconds <= 5
  const progress = (seconds / 60) * 100
  const circumference = 2 * Math.PI * 45

  return (
    <section className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-slate-800/90 to-slate-900/90 border border-slate-700/50 backdrop-blur-xl">
      {/* Animated background glow */}
      <div 
        className={`absolute inset-0 transition-opacity duration-500 ${
          isUrgent ? 'opacity-100' : 'opacity-0'
        }`}
      >
        <div className={`absolute inset-0 bg-gradient-to-br ${
          isCritical 
            ? 'from-rose-500/20 via-transparent to-rose-500/10' 
            : 'from-amber-500/15 via-transparent to-amber-500/10'
        }`} />
      </div>

      <div className="relative p-6 lg:p-10">
        {/* Event info */}
        <div className="text-center mb-6 lg:mb-8">
          <h2 className={`font-bold text-xl lg:text-3xl mb-1 ${
            isCritical ? 'text-rose-400' : isUrgent ? 'text-amber-400' : 'text-white'
          }`}>
            {eventTypeLabels[eventType]}
          </h2>
          <p className="text-slate-400 text-sm lg:text-lg">
            {eventTypeDetails[eventType](eventValue)}
          </p>
        </div>

        {/* Countdown circle - THE STAR */}
        <div className="relative w-48 h-48 lg:w-80 lg:h-80 mx-auto mb-6 lg:mb-10">
          {/* Outer glow ring */}
          <div 
            className={`absolute inset-0 rounded-full transition-all duration-300 ${
              isCritical 
                ? 'shadow-[0_0_60px_rgba(244,63,94,0.4)]' 
                : isUrgent 
                  ? 'shadow-[0_0_40px_rgba(251,191,36,0.3)]' 
                  : 'shadow-[0_0_30px_rgba(139,92,246,0.2)]'
            }`} 
          />
          
          <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
            <defs>
              <linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor={isCritical ? '#f43f5e' : isUrgent ? '#fbbf24' : '#06b6d4'} />
                <stop offset="100%" stopColor={isCritical ? '#e11d48' : isUrgent ? '#f59e0b' : '#8b5cf6'} />
              </linearGradient>
            </defs>
            
            {/* Background track */}
            <circle
              cx="50"
              cy="50"
              r="45"
              fill="none"
              stroke="rgba(255,255,255,0.05)"
              strokeWidth="4"
            />
            
            {/* Progress arc */}
            <circle
              cx="50"
              cy="50"
              r="45"
              fill="none"
              stroke="url(#progressGradient)"
              strokeWidth="4"
              strokeLinecap="round"
              strokeDasharray={circumference}
              strokeDashoffset={circumference - (progress / 100) * circumference}
              className="transition-all duration-1000 ease-linear"
              style={{ 
                filter: isUrgent ? 'drop-shadow(0 0 12px currentColor)' : 'none'
              }}
            />
          </svg>

          {/* Center content */}
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span
              className={`font-black tracking-tighter transition-all duration-300 ${
                isCritical 
                  ? 'text-7xl lg:text-[11rem] text-rose-400' 
                  : isUrgent 
                    ? 'text-7xl lg:text-[11rem] text-amber-400' 
                    : 'text-6xl lg:text-[10rem] text-white'
              } ${isUrgent ? 'animate-pulse' : ''}`}
            >
              {seconds}
            </span>
            <span className={`text-sm lg:text-xl uppercase tracking-[0.2em] font-medium mt-1 lg:mt-2 ${
              isCritical ? 'text-rose-400/70' : isUrgent ? 'text-amber-400/70' : 'text-slate-500'
            }`}>
              segundos
            </span>
          </div>
        </div>

        {/* Helper text */}
        <p className={`text-center text-sm lg:text-base ${
          isUrgent ? 'text-amber-400/80' : 'text-slate-500'
        }`}>
          {isUrgent 
            ? 'Confirma pronto para evitar notificar contactos' 
            : 'Si nadie confirma, notificaremos automaticamente'
          }
        </p>
      </div>
    </section>
  )
}
