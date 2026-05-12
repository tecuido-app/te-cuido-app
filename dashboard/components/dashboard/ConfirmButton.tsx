'use client'

type ConfirmButtonProps = {
  patientName: string
  onConfirm: () => void
}

function CheckIcon({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="3"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <polyline points="20 6 9 17 4 12" />
    </svg>
  )
}

export function ConfirmButton({ patientName, onConfirm }: ConfirmButtonProps) {
  const firstName = patientName.split(' ')[0]

  return (
    <button
      onClick={onConfirm}
      className="group relative w-full overflow-hidden rounded-2xl transition-all duration-200 active:scale-[0.98]"
    >
      {/* Gradient background */}
      <div className="absolute inset-0 bg-gradient-to-r from-cyan-500 via-violet-500 to-fuchsia-500 transition-all duration-300 group-hover:scale-105" />
      
      {/* Shine effect */}
      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-700" />
      
      {/* Content */}
      <div className="relative flex items-center justify-center gap-3 lg:gap-4 py-5 lg:py-7 px-6 lg:px-8">
        <div className="w-8 h-8 lg:w-10 lg:h-10 rounded-full bg-white/20 flex items-center justify-center backdrop-blur-sm">
          <CheckIcon className="w-5 h-5 lg:w-6 lg:h-6 text-white" />
        </div>
        <span className="text-white font-bold text-lg lg:text-2xl tracking-tight">
          {firstName} esta bien
        </span>
      </div>
    </button>
  )
}
