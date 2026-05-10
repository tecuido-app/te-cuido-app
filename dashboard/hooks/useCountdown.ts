'use client'

import { useState, useEffect, useCallback } from 'react'

export function useCountdown(
  initialSeconds: number,
  isActive: boolean,
  onComplete: () => void
) {
  const [seconds, setSeconds] = useState(initialSeconds)

  const reset = useCallback((newSeconds?: number) => {
    setSeconds(newSeconds ?? initialSeconds)
  }, [initialSeconds])

  useEffect(() => {
    if (!isActive) return

    if (seconds <= 0) {
      onComplete()
      return
    }

    const timer = setInterval(() => {
      setSeconds((prev) => {
        if (prev <= 1) {
          clearInterval(timer)
          return 0
        }
        return prev - 1
      })
    }, 1000)

    return () => clearInterval(timer)
  }, [isActive, seconds, onComplete])

  return { seconds, reset }
}
