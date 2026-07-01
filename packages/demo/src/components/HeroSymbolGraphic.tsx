import { cn } from '../lib/cn'

type HeroSymbolGraphicProps = {
  symbolId: string
  className?: string
}

/** Premium slot-symbol artwork for the hero marketing demo. */
export function HeroSymbolGraphic({ symbolId, className }: HeroSymbolGraphicProps) {
  const uid = symbolId.toLowerCase().replace(/[^a-z0-9]/g, '')

  return (
    <svg
      viewBox="0 0 48 48"
      className={cn('hero-symbol-graphic', className)}
      aria-hidden
    >
      {symbolId === 'HV1' && <CrownGraphic uid={uid} />}
      {symbolId === 'HV2' && <ShieldGraphic uid={uid} />}
      {symbolId === 'LV1' && <AceGraphic uid={uid} />}
      {symbolId === 'LV2' && <KingGraphic uid={uid} />}
      {symbolId === 'WILD' && <CloverGraphic uid={uid} />}
      {symbolId === 'SCAT' && <ScatterGraphic uid={uid} />}
      {symbolId === 'BONUS' && <CloverGraphic uid={uid} />}
    </svg>
  )
}

function CrownGraphic({ uid }: { uid: string }) {
  return (
    <>
      <defs>
        <linearGradient id={`${uid}-gold`} x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#fde68a" />
          <stop offset="55%" stopColor="#f59e0b" />
          <stop offset="100%" stopColor="#b45309" />
        </linearGradient>
        <linearGradient id={`${uid}-band`} x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="#92400e" />
          <stop offset="100%" stopColor="#78350f" />
        </linearGradient>
      </defs>
      <path
        d="M8 30h32l-2.5-11-7 6.5-5.5-10-5.5 10-7-6.5L8 30z"
        fill={`url(#${uid}-gold)`}
        stroke="#fcd34d"
        strokeWidth="0.75"
      />
      <rect x="10" y="30" width="28" height="5" rx="1.5" fill={`url(#${uid}-band)`} />
      <circle cx="14" cy="32.5" r="1.4" fill="#ef4444" />
      <circle cx="24" cy="32.5" r="1.6" fill="#dc2626" />
      <circle cx="34" cy="32.5" r="1.4" fill="#ef4444" />
      <circle cx="19" cy="21" r="1.1" fill="#fecaca" />
      <circle cx="29" cy="21" r="1.1" fill="#fecaca" />
    </>
  )
}

function KingGraphic({ uid }: { uid: string }) {
  return (
    <>
      <defs>
        <linearGradient id={`${uid}-gold`} x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#fde68a" />
          <stop offset="100%" stopColor="#d97706" />
        </linearGradient>
      </defs>
      <path
        d="M12 31h24l-1.5-8-4.5 4-3.5-6.5-3.5 6.5-4.5-4L12 31z"
        fill={`url(#${uid}-gold)`}
        stroke="#fcd34d"
        strokeWidth="0.6"
      />
      <rect x="13.5" y="31" width="21" height="3.5" rx="1" fill="#92400e" />
      <circle cx="24" cy="33" r="1" fill="#ef4444" />
    </>
  )
}

function ShieldGraphic({ uid }: { uid: string }) {
  return (
    <>
      <defs>
        <linearGradient id={`${uid}-shield`} x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#60a5fa" />
          <stop offset="100%" stopColor="#1d4ed8" />
        </linearGradient>
        <linearGradient id={`${uid}-rim`} x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="#fde68a" />
          <stop offset="100%" stopColor="#d97706" />
        </linearGradient>
      </defs>
      <path
        d="M24 7l12 5v11c0 9.5-5.5 15.5-12 18-6.5-2.5-12-8.5-12-18V12l12-5z"
        fill={`url(#${uid}-shield)`}
        stroke={`url(#${uid}-rim)`}
        strokeWidth="2"
      />
      <path
        d="M24 14v16M18 20h12"
        stroke="#fde68a"
        strokeWidth="2.2"
        strokeLinecap="round"
      />
    </>
  )
}

function AceGraphic({ uid }: { uid: string }) {
  return (
    <>
      <defs>
        <linearGradient id={`${uid}-gem`} x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#fca5a5" />
          <stop offset="45%" stopColor="#ef4444" />
          <stop offset="100%" stopColor="#991b1b" />
        </linearGradient>
      </defs>
      <path
        d="M24 8l11 7.5v9L24 38 13 24.5v-9L24 8z"
        fill={`url(#${uid}-gem)`}
        stroke="#fecaca"
        strokeWidth="0.8"
      />
      <path d="M24 11 17 24.5h14L24 11z" fill="#ffffff22" />
      <text
        x="24"
        y="27"
        textAnchor="middle"
        fill="#fff"
        fontSize="11"
        fontWeight="700"
        fontFamily="ui-sans-serif, system-ui, sans-serif"
      >
        A
      </text>
    </>
  )
}

function CloverGraphic({ uid }: { uid: string }) {
  return (
    <>
      <defs>
        <radialGradient id={`${uid}-leaf`} cx="35%" cy="30%" r="65%">
          <stop offset="0%" stopColor="#86efac" />
          <stop offset="100%" stopColor="#15803d" />
        </radialGradient>
      </defs>
      <circle cx="18" cy="18" r="7" fill={`url(#${uid}-leaf)`} />
      <circle cx="30" cy="18" r="7" fill={`url(#${uid}-leaf)`} />
      <circle cx="18" cy="30" r="7" fill={`url(#${uid}-leaf)`} />
      <circle cx="30" cy="30" r="7" fill={`url(#${uid}-leaf)`} />
      <rect x="22.5" y="28" width="3" height="12" rx="1.5" fill="#166534" />
    </>
  )
}

function ScatterGraphic({ uid }: { uid: string }) {
  return (
    <>
      <defs>
        <linearGradient id={`${uid}-diamond`} x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#93c5fd" />
          <stop offset="50%" stopColor="#3b82f6" />
          <stop offset="100%" stopColor="#1e40af" />
        </linearGradient>
      </defs>
      <path
        d="M24 9l12 12-12 18L12 21 24 9z"
        fill={`url(#${uid}-diamond)`}
        stroke="#bfdbfe"
        strokeWidth="0.8"
      />
      <path d="M24 12 15 21h18L24 12z" fill="#ffffff28" />
    </>
  )
}

/** Sidebar subtitle — Wild maps to Bonus per marketing reference. */
export function getHeroPaletteSubtitle(symbolId: string): string {
  if (symbolId === 'WILD') return 'Bonus'
  return symbolId
}
