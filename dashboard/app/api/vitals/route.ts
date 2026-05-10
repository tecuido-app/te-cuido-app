import { NextResponse } from 'next/server'

// Box-Muller: normal distribution N(mean, std)
function gaussian(mean: number, std: number): number {
  const u1 = Math.random()
  const u2 = Math.random()
  const z = Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2)
  return mean + z * std
}

function clamp(value: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, value))
}

export function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const status = searchParams.get('status') ?? 'ok'

  let heartRate: number
  let spo2: number
  let skinTemp: number

  if (status === 'emergency') {
    heartRate = Math.round(clamp(gaussian(35, 3), 26, 44))
    spo2 = Math.round(clamp(gaussian(86, 2), 80, 91))
    skinTemp = Math.round(clamp(gaussian(36.1, 0.15), 35.6, 36.6) * 10) / 10
  } else if (status === 'alert') {
    heartRate = Math.round(clamp(gaussian(40, 3), 32, 49))
    spo2 = Math.round(clamp(gaussian(94, 1.5), 90, 96))
    skinTemp = Math.round(clamp(gaussian(36.4, 0.15), 35.9, 36.9) * 10) / 10
  } else {
    heartRate = Math.round(clamp(gaussian(72, 5), 58, 88))
    spo2 = Math.round(clamp(gaussian(97, 1), 95, 100))
    skinTemp = Math.round(clamp(gaussian(36.6, 0.2), 36.0, 37.2) * 10) / 10
  }

  return NextResponse.json({
    heartRate,
    spo2,
    skinTemp,
    timestamp: new Date().toISOString(),
  })
}
