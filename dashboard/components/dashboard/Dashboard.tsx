'use client'

import { useState, useCallback, useEffect, useRef } from 'react'
import type { DashboardData, Status, Vitals } from '@/lib/types'
import { mockOk, mockAlert, mockEmergency } from '@/lib/mockData'
import { useCountdown } from '@/hooks/useCountdown'
import { StatusHeader } from './StatusHeader'
import { VitalsDisplay } from './VitalsDisplay'
import { CountdownTimer } from './CountdownTimer'
import { ConfirmButton } from './ConfirmButton'
import { EventTimeline } from './EventTimeline'
import { HistoryList } from './HistoryList'
import { DevModeToggle } from './DevModeToggle'
import { EmergencyBanner } from './EmergencyBanner'

const AGENT_URL = process.env.NEXT_PUBLIC_AGENT_URL ?? 'http://localhost:8000'

const dataByStatus: Record<Status, DashboardData> = {
  ok: mockOk,
  alert: mockAlert,
  emergency: mockEmergency,
}

function WifiIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M5 12.55a11 11 0 0 1 14.08 0" />
      <path d="M1.42 9a16 16 0 0 1 21.16 0" />
      <path d="M8.53 16.11a6 6 0 0 1 6.95 0" />
      <line x1="12" y1="20" x2="12.01" y2="20" />
    </svg>
  )
}

function ShieldCheckIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
      <polyline points="9 12 12 15 16 10" />
    </svg>
  )
}

function OkStatusMessage() {
  return (
    <section className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-slate-800/80 to-slate-900/80 p-8 lg:p-12 text-center border border-slate-700/50 backdrop-blur-xl">
      <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/10 via-transparent to-violet-500/10 pointer-events-none" />
      <div className="relative">
        <div className="w-20 h-20 lg:w-28 lg:h-28 rounded-full bg-gradient-to-br from-cyan-400 to-violet-500 flex items-center justify-center mx-auto mb-6 shadow-2xl shadow-cyan-500/25">
          <ShieldCheckIcon className="w-10 h-10 lg:w-14 lg:h-14 text-white" />
        </div>
        <div className="flex items-center justify-center gap-2 mb-3">
          <WifiIcon className="w-4 h-4 lg:w-5 lg:h-5 text-cyan-400 animate-pulse" />
          <span className="text-xs lg:text-sm font-medium text-cyan-400 uppercase tracking-widest">
            Online
          </span>
        </div>
        <h2 className="text-white font-bold text-2xl lg:text-4xl mb-3 tracking-tight">
          System active
        </h2>
        <p className="text-slate-400 text-base lg:text-xl max-w-md mx-auto leading-relaxed">
          Monitoring vital signs. We'll alert you if we detect anything.
        </p>
      </div>
    </section>
  )
}

export function Dashboard() {
  // ── Agent connection ──────────────────────────────────────────────
  const [agentData, setAgentData] = useState<DashboardData | null>(null)
  const [agentOnline, setAgentOnline] = useState(false)

  useEffect(() => {
    let cancelled = false
    async function poll() {
      try {
        const res = await fetch('/api/agent-status')
        if (!res.ok) throw new Error()
        const d = await res.json()
        if (!cancelled) { setAgentData(d); setAgentOnline(true) }
      } catch {
        if (!cancelled) setAgentOnline(false)
      }
    }
    poll()
    const id = setInterval(poll, 3000)
    return () => { cancelled = true; clearInterval(id) }
  }, [])

  // ── State (real agent or local mock) ──────────────────────────────
  const [mockStatus, setMockStatus] = useState<Status>('ok')
  const status: Status = agentOnline ? (agentData?.status ?? 'ok') : mockStatus

  const activeEvent = agentOnline
    ? (agentData?.activeEvent ?? null)
    : dataByStatus[mockStatus].activeEvent

  const history = agentOnline
    ? (agentData?.history ?? [])
    : dataByStatus[mockStatus].history

  const patientName = agentOnline
    ? (agentData?.patientName ?? 'Carmen Garcia')
    : dataByStatus[mockStatus].patientName

  const patientAge = agentOnline
    ? (agentData?.patientAge ?? 78)
    : dataByStatus[mockStatus].patientAge

  // ── Vitals vivas desde /api/vitals ─────────────────────────────────
  const [vitals, setVitals] = useState<Vitals>(mockOk.vitals)

  useEffect(() => {
    let cancelled = false
    async function fetchVitals() {
      try {
        const res = await fetch(`/api/vitals?status=${status}`)
        if (!res.ok) return
        const v: Vitals = await res.json()
        if (!cancelled) setVitals(v)
      } catch { /* keep last value */ }
    }
    fetchVitals()
    const id = setInterval(fetchVitals, 5000)
    return () => { cancelled = true; clearInterval(id) }
  }, [status])

  // ── Countdown ──────────────────────────────────────────────────────
  const prevStatusRef = useRef<Status>(status)

  const handleCountdownComplete = useCallback(() => {
    if (!agentOnline) setMockStatus('emergency')
    // If the agent is online, it handles the transition — polling detects it
  }, [agentOnline])

  const { seconds, reset } = useCountdown(60, status === 'alert', handleCountdownComplete)

  useEffect(() => {
    if (status === 'alert' && prevStatusRef.current !== 'alert') {
      const init = agentData?.graceSecondsRemaining ?? 60
      reset(init)
    }
    prevStatusRef.current = status
  }, [status, agentData?.graceSecondsRemaining, reset])

  // ── Acciones ────────────────────────────────────────────────────────
  const handleWellbeingConfirm = useCallback(async () => {
    if (agentOnline) {
      await fetch(`${AGENT_URL}/api/wellbeing`, { method: 'POST' }).catch(() => {})
      // Polling will detect the status change in ~3s
    } else {
      setMockStatus('ok')
    }
  }, [agentOnline])

  const handleDevCycle = useCallback(() => {
    setMockStatus((current) => {
      let next: Status
      if (current === 'ok') { reset(60); next = 'alert' }
      else if (current === 'alert') { next = 'emergency' }
      else { reset(60); next = 'ok' }
      setVitals(dataByStatus[next].vitals)
      return next
    })
  }, [reset])

  return (
    <div className="min-h-screen bg-slate-950">
      <div className="fixed inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-slate-900 via-slate-950 to-black pointer-events-none" />
      <div className="fixed inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxwYXRoIGQ9Ik0wIDBoNjB2NjBIMHoiLz48cGF0aCBkPSJNMzAgMzBtLTEgMGExIDEgMCAxIDAgMiAwYTEgMSAwIDEgMCAtMiAwIiBmaWxsPSJyZ2JhKDI1NSwyNTUsMjU1LDAuMDMpIi8+PC9nPjwvc3ZnPg==')] opacity-50 pointer-events-none" />

      <main className="relative max-w-lg lg:max-w-2xl mx-auto px-5 lg:px-8 py-8 lg:py-16 space-y-8 lg:space-y-10">
        {/* Logo */}
        <header className="flex justify-between items-center">
          <img
            src="/logo-tecuido.png"
            alt="Te Cuido"
            className="h-14 lg:h-20 w-auto drop-shadow-2xl"
          />
          {/* Agent connection indicator */}
          <div className={`flex items-center gap-1.5 text-xs font-medium px-2.5 py-1 rounded-full border transition-all duration-500 ${
            agentOnline
              ? 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10'
              : 'text-slate-500 border-slate-700/50 bg-slate-800/30'
          }`}>
            <span className={`w-1.5 h-1.5 rounded-full ${agentOnline ? 'bg-emerald-400 animate-pulse' : 'bg-slate-600'}`} />
            {agentOnline ? 'Agent connected' : 'Demo'}
          </div>
        </header>

        <StatusHeader
          patientName={patientName}
          patientAge={patientAge}
          status={status}
        />

        {status === 'ok' && <OkStatusMessage />}

        {status === 'alert' && activeEvent && (
          <div className="space-y-6 lg:space-y-8">
            <CountdownTimer
              seconds={seconds}
              eventType={activeEvent.type}
              eventValue={activeEvent.value}
            />
            <ConfirmButton
              patientName={patientName}
              onConfirm={handleWellbeingConfirm}
            />
            <EventTimeline
              actions={activeEvent.actions}
              isEmergency={false}
            />
          </div>
        )}

        {status === 'emergency' && activeEvent && (
          <div className="space-y-6 lg:space-y-8">
            <EmergencyBanner eventType={activeEvent.type} />
            <EventTimeline
              actions={activeEvent.actions}
              isEmergency={true}
            />
          </div>
        )}

        <VitalsDisplay vitals={vitals} status={status} />

        <HistoryList events={history} />

        <footer className="pt-4 text-center">
          <p className="text-slate-600 text-xs lg:text-sm">
            Every action recorded on Solana
          </p>
        </footer>
      </main>

    </div>
  )
}
