'use client'

import type { AgentAction, ActionType } from '@/lib/types'

type EventTimelineProps = {
  actions: AgentAction[]
  isEmergency: boolean
}

function ExternalLinkIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6" />
      <polyline points="15 3 21 3 21 9" />
      <line x1="10" y1="14" x2="21" y2="3" />
    </svg>
  )
}

const actionLabels: Record<ActionType, string> = {
  GracePeriod: 'Grace period started',
  NotifiedContact: 'Contact notified',
  Escalated: 'Escalating to emergency',
  WellbeingConfirmed: 'Wellbeing confirmed',
  Resolved: 'Event resolved',
}

const actionIcons: Record<ActionType, string> = {
  GracePeriod: '⏱',
  NotifiedContact: '📱',
  Escalated: '🚨',
  WellbeingConfirmed: '✓',
  Resolved: '✓',
}

function formatTimeAgo(isoString: string): string {
  const now = new Date()
  const then = new Date(isoString)
  const diffMs = now.getTime() - then.getTime()
  const diffSecs = Math.floor(diffMs / 1000)

  if (diffSecs < 60) return `${diffSecs}s`
  
  const diffMins = Math.floor(diffSecs / 60)
  if (diffMins < 60) return `${diffMins}m`

  const diffHours = Math.floor(diffMins / 60)
  return `${diffHours}h`
}

function getSolanaExplorerUrl(txHash: string): string {
  return `https://explorer.solana.com/tx/${txHash}?cluster=devnet`
}

export function EventTimeline({ actions, isEmergency }: EventTimelineProps) {
  if (actions.length === 0) return null

  return (
    <section className="space-y-3">
      <h2 className="text-sm lg:text-base font-semibold text-slate-400 uppercase tracking-wider">
        {isEmergency ? 'System actions' : 'Activity'}
      </h2>
      
      <div className={`rounded-2xl overflow-hidden border ${
        isEmergency 
          ? 'bg-rose-500/10 border-rose-500/30' 
          : 'bg-slate-800/50 border-slate-700/50'
      }`}>
        {actions.map((action, index) => (
          <div
            key={`${action.txHash}-${index}`}
            className={`flex items-center gap-4 px-4 lg:px-5 py-3.5 lg:py-4 ${
              index !== actions.length - 1 ? 'border-b border-slate-700/30' : ''
            }`}
          >
            <div className={`w-9 h-9 lg:w-10 lg:h-10 rounded-xl flex items-center justify-center text-lg ${
              isEmergency ? 'bg-rose-500/20' : 'bg-slate-700/50'
            }`}>
              {actionIcons[action.type]}
            </div>
            
            <div className="flex-1 min-w-0">
              <span className={`font-medium text-sm lg:text-base block ${
                isEmergency ? 'text-rose-200' : 'text-white'
              }`}>
                {action.note || actionLabels[action.type]}
              </span>
              <div className="flex items-center gap-2 mt-0.5">
                <span className="text-xs lg:text-sm text-slate-500">
                  {formatTimeAgo(action.timestamp)}
                </span>
                <span className="text-slate-700">•</span>
                <a
                  href={getSolanaExplorerUrl(action.txHash)}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={`inline-flex items-center gap-1 text-xs lg:text-sm hover:underline ${
                    isEmergency ? 'text-rose-400' : 'text-cyan-400'
                  }`}
                >
                  Solana
                  <ExternalLinkIcon className="w-3 h-3" />
                </a>
              </div>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}
