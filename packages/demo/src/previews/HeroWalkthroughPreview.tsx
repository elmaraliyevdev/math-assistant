'use client'

import {
  getHeroPaletteSubtitle,
  HeroSymbolGraphic,
} from '../components/HeroSymbolGraphic'
import type { HeroValidationStatus } from '../hooks/use-hero-walkthrough'
import { cn } from '../lib/cn'
import { HERO_PALETTE, HERO_REELS, HERO_SYMBOL_META } from '../data/hero-reels'

export type HeroWalkthroughPreviewProps = {
  draggingSymbol?: string | null
  showDragPath?: boolean
  showDropZone?: boolean
  placedSymbol?: string | null
  dropTargetReel?: number
  dropSlotIndex?: number
  activePaletteSymbol?: string | null
  validationStatus?: HeroValidationStatus
  rtp?: number
  distribution?: {
    wild: number
    scatter: number
    holdWin: number
    hitFrequency: number
  }
  showConstraintsPass?: boolean
}

export function HeroWalkthroughPreview({
  draggingSymbol,
  showDragPath,
  showDropZone,
  placedSymbol,
  dropTargetReel,
  dropSlotIndex,
  activePaletteSymbol,
  validationStatus,
  rtp = 95.94,
  distribution = { wild: 8.1, scatter: 2.4, holdWin: 1.2, hitFrequency: 32.2 },
  showConstraintsPass,
}: HeroWalkthroughPreviewProps) {
  return (
    <div className="hero-studio">
      <aside className="hero-studio__symbols" aria-hidden>
        <p className="hero-studio__section-label">Symbols</p>
        <ul className="hero-studio__symbol-list">
          {HERO_PALETTE.map((symbolId) => {
            const meta = HERO_SYMBOL_META[symbolId]
            const subtitle = getHeroPaletteSubtitle(symbolId)
            const isActive = activePaletteSymbol === symbolId
            const isDragging = draggingSymbol === symbolId
            return (
              <li
                key={symbolId}
                className={cn(
                  'hero-studio__symbol-card',
                  isActive && 'hero-studio__symbol-card--active',
                  isDragging && 'hero-studio__symbol-card--dragging',
                )}
              >
                <span className="hero-studio__grip" aria-hidden>
                  <span />
                  <span />
                  <span />
                  <span />
                  <span />
                  <span />
                </span>
                <span className="hero-studio__chip">
                  <HeroSymbolGraphic symbolId={symbolId} />
                </span>
                <span className="hero-studio__symbol-copy">
                  <span className="hero-studio__symbol-name">{meta.displayName}</span>
                  <span
                    className={cn(
                      'hero-studio__symbol-code',
                      symbolId === 'WILD' && 'hero-studio__symbol-code--bonus',
                    )}
                  >
                    {subtitle}
                  </span>
                </span>
              </li>
            )
          })}
        </ul>
        <p className="hero-studio__hint">
          <span className="hero-studio__hint-icon" aria-hidden>
            <svg viewBox="0 0 16 16" width="12" height="12" fill="currentColor">
              <path d="M2 14h1.5V6H2V4.5h3V3H2V1.5h4.5V14H2zm7.5 0h1.5V8.5L13 6.5l1 1-3.25 3.5L14 14h-1.75l-2-3.25L8.5 14z" />
            </svg>
          </span>
          Drag a symbol onto any reel position
        </p>
      </aside>

      <div className="hero-studio__workspace">
        <header className="hero-studio__strips-header">
          <p className="hero-studio__section-label">Reel strips</p>
          <p className="hero-studio__strips-meta">Base game · 5 reels · 7 positions</p>
        </header>

        <div className="hero-studio__reels-wrap">
          {showDragPath ? (
            <svg className="hero-studio__drag-path" viewBox="0 0 360 140" aria-hidden>
              <defs>
                <linearGradient id="hero-drag-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="oklch(0.62 0.19 255 / 0.12)" />
                  <stop offset="100%" stopColor="oklch(0.62 0.19 255 / 0.95)" />
                </linearGradient>
              </defs>
              <path
                className="hero-studio__drag-path-line"
                d="M 12 72 C 88 28, 168 108, 268 62"
                fill="none"
                stroke="url(#hero-drag-gradient)"
                strokeWidth="3.5"
                strokeLinecap="round"
              />
              <polygon
                className="hero-studio__drag-path-arrow"
                points="268,62 256,56 259,66"
                fill="oklch(0.62 0.19 255)"
              />
            </svg>
          ) : null}

          <div className="hero-studio__reels">
            {HERO_REELS.map((reel, reelIndex) => (
              <div key={reelIndex} className="hero-studio__reel">
                <p className="hero-studio__reel-label">Reel {reelIndex + 1}</p>
                <div className="hero-studio__reel-track">
                  {reel.map((symbolId, slotIndex) => {
                    const isDropSlot =
                      dropTargetReel === reelIndex && dropSlotIndex === slotIndex
                    const showEmptyDrop = isDropSlot && showDropZone && !placedSymbol
                    const showPlaced = isDropSlot && placedSymbol

                    if (showEmptyDrop) {
                      return (
                        <div
                          key={`${reelIndex}-${slotIndex}`}
                          className="hero-studio__slot hero-studio__slot--drop"
                        />
                      )
                    }

                    const graphicId = showPlaced ? placedSymbol : symbolId

                    return (
                      <div
                        key={`${reelIndex}-${slotIndex}`}
                        className={cn(
                          'hero-studio__slot',
                          showPlaced && 'hero-studio__slot--placed',
                          validationStatus === 'checking' &&
                            isDropSlot &&
                            'hero-studio__slot--checking',
                        )}
                      >
                        <HeroSymbolGraphic symbolId={graphicId} />
                      </div>
                    )
                  })}
                </div>
              </div>
            ))}
          </div>

          {draggingSymbol ? (
            <div className="hero-studio__drag-ghost" aria-hidden>
              <div className="hero-studio__slot hero-studio__slot--ghost">
                <HeroSymbolGraphic symbolId={draggingSymbol} />
              </div>
            </div>
          ) : null}
        </div>
      </div>

      <aside className="hero-studio__panel" aria-hidden>
        <div className="hero-studio__panel-badges">
          <span className="hero-studio__badge hero-studio__badge--rtp tabular-nums">
            RTP {rtp.toFixed(2)}%
          </span>
          <span
            className={cn(
              'hero-studio__badge hero-studio__badge--pass',
              showConstraintsPass && 'hero-studio__badge--pass-active',
            )}
          >
            ✓ Constraints PASS
          </span>
        </div>

        <div className="hero-studio__panel-block">
          <p className="hero-studio__section-label">Distribution</p>
          <DistributionRow label="Wild" value={distribution.wild} />
          <DistributionRow label="Scatter" value={distribution.scatter} />
          <DistributionRow label="Hold & Win" value={distribution.holdWin} />
          <DistributionRow label="Hit frequency" value={distribution.hitFrequency} wide />
        </div>

        <div className="hero-studio__panel-block">
          <p className="hero-studio__section-label">Live feedback</p>
          <div
            className={cn(
              'hero-studio__feedback-hero',
              validationStatus === 'checking' && 'hero-studio__feedback-hero--checking',
              showConstraintsPass && 'hero-studio__feedback-hero--visible',
            )}
          >
            <span className="hero-studio__feedback-hero-icon">✓</span>
            <div>
              <span className="hero-studio__feedback-hero-label">Constraints</span>
              <span className="hero-studio__feedback-hero-pass">PASS</span>
            </div>
          </div>
          <div className="hero-studio__rtp-card">
            <span className="hero-studio__rtp-label">Theoretical RTP</span>
            <span className="hero-studio__rtp-value tabular-nums">{rtp.toFixed(2)}%</span>
          </div>
        </div>
      </aside>
    </div>
  )
}

function DistributionRow({
  label,
  value,
  wide,
}: {
  label: string
  value: number
  wide?: boolean
}) {
  const width = wide ? Math.min(value, 100) : Math.min(value * 5.5, 100)

  return (
    <div className="hero-studio__dist-row">
      <div className="hero-studio__dist-head">
        <span>{label}</span>
        <span className="tabular-nums">{value.toFixed(1)}%</span>
      </div>
      <div className="hero-studio__dist-track">
        <div className="hero-studio__dist-fill" style={{ width: `${width}%` }} />
      </div>
    </div>
  )
}
