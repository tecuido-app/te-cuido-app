import { NextResponse } from 'next/server'

const AGENT_URL = process.env.NEXT_PUBLIC_AGENT_URL ?? 'http://localhost:8000'
const AGENT_API_KEY = process.env.AGENT_API_KEY ?? ''

export async function POST() {
  try {
    const res = await fetch(`${AGENT_URL}/api/wellbeing`, {
      method: 'POST',
      cache: 'no-store',
      headers: AGENT_API_KEY ? { 'x-demo-api-key': AGENT_API_KEY } : {},
      signal: AbortSignal.timeout(5000),
    })

    if (!res.ok) {
      return NextResponse.json({ error: 'agent_error' }, { status: res.status })
    }

    return NextResponse.json(await res.json())
  } catch {
    return NextResponse.json({ error: 'agent_offline' }, { status: 503 })
  }
}
