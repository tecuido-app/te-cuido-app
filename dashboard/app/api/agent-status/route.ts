import { NextResponse } from 'next/server'

const AGENT_URL = process.env.NEXT_PUBLIC_AGENT_URL ?? 'http://localhost:8000'

function mapAction(a: Record<string, unknown>) {
  return {
    type: a.type,
    timestamp: a.timestamp,
    txHash: (a.tx_hash as string) ?? '',
    contactIndex: a.contact_index != null ? (a.contact_index as number) : undefined,
    note: (a.note as string) ?? undefined,
  }
}

function mapEvent(e: Record<string, unknown> | null) {
  if (!e) return null
  return {
    id: e.id,
    type: e.type,
    severity: e.severity,
    value: e.value,
    timestamp: e.timestamp,
    actions: ((e.actions as unknown[]) ?? []).map((a) =>
      mapAction(a as Record<string, unknown>)
    ),
    resolved: e.resolved,
    resolvedAt: (e.resolved_at as string) ?? undefined,
  }
}

export async function GET() {
  try {
    const res = await fetch(`${AGENT_URL}/api/status`, {
      cache: 'no-store',
      signal: AbortSignal.timeout(2000),
    })
    if (!res.ok) throw new Error(`agent ${res.status}`)

    const d = await res.json()

    const vitals = d.vitals
      ? {
          heartRate: d.vitals.heart_rate,
          spo2: d.vitals.spo2,
          skinTemp: d.vitals.skin_temp,
          timestamp: d.vitals.timestamp ?? new Date().toISOString(),
        }
      : null

    return NextResponse.json({
      status: d.status,
      patientName: d.patient?.name ?? 'Carmen García',
      patientAge: d.patient?.age ?? 78,
      vitals,
      activeEvent: mapEvent(d.active_event),
      history: ((d.history as unknown[]) ?? [])
        .map((e) => mapEvent(e as Record<string, unknown>))
        .filter(Boolean),
      graceSecondsRemaining: d.grace_seconds_remaining ?? null,
    })
  } catch {
    return NextResponse.json({ error: 'agent_offline' }, { status: 503 })
  }
}
