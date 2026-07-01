'use client'

import { Badge } from '@/components/ui/badge'

import { demoCalibrateResponse } from '../data/mathematics'
import { useReelStudioPreview } from '../hooks/use-reel-studio-preview'
import { cn } from '../lib/cn'
import { HERO_REELS, HERO_SYMBOL_CLASS, HERO_SYMBOL_META } from '../data/hero-reels'

import '../styles/reel-strips-marketing.css'

const STRIP_PREVIEW_LENGTH = 6

/** Horizontal strip editor + live distribution — not the hero column grid. */
export function ReelStudioPreview() {
  const {
    activeReel,
    showInsertion,
    scatterPercent,
    wildPercent,
    crownPercent,
    showPass,
    caption,
  } = useReelStudioPreview()
  const theoreticalRtp = demoCalibrateResponse.calibration.theoreticalRtp ?? 95.98

  return (
    <div className="strip-marketing">
      <div className="strip-marketing__header">
        <p className="strip-marketing__caption">{caption}</p>
        <div className="strip-marketing__badges">
          <Badge variant="secondary" className="strip-marketing__badge">
            RTP {theoreticalRtp.toFixed(2)}%
          </Badge>
          <Badge
            variant="success"
            className={cn('strip-marketing__badge', showPass && 'strip-marketing__badge--pop')}
          >
            Constraints PASS
          </Badge>
        </div>
      </div>

      <div className="strip-marketing__body">
        <div className="strip-marketing__strips">
          {HERO_REELS.map((reel, reelIndex) => {
            const symbols = reel.slice(0, STRIP_PREVIEW_LENGTH)
            const isActive = activeReel === reelIndex
            return (
              <div
                key={reelIndex}
                className={cn(
                  'strip-marketing__row',
                  isActive && 'strip-marketing__row--active',
                )}
              >
                <span className="strip-marketing__row-label">Reel {reelIndex + 1}</span>
                <div className="strip-marketing__row-track">
                  {symbols.map((symbolId, index) => {
                    const meta = HERO_SYMBOL_META[symbolId]
                    return (
                      <span
                        key={`${reelIndex}-${index}`}
                        className={cn(
                          'strip-marketing__chip',
                          HERO_SYMBOL_CLASS[meta.type],
                        )}
                      >
                        {meta.displayName}
                      </span>
                    )
                  })}
                  {isActive && showInsertion ? (
                    <span
                      className={cn(
                        'strip-marketing__chip strip-marketing__chip--insert',
                        HERO_SYMBOL_CLASS.scatter,
                      )}
                    >
                      Scatter
                    </span>
                  ) : null}
                </div>
              </div>
            )
          })}
        </div>

        <aside className="strip-marketing__distribution">
          <p className="strip-marketing__distribution-title">Live distribution</p>
          <DistributionBar
            label="Scatter"
            percent={scatterPercent}
            tone="scatter"
            emphasize={showPass}
          />
          <DistributionBar label="Wild" percent={wildPercent} tone="wild" />
          <DistributionBar label="Crown" percent={crownPercent} tone="regular" />
        </aside>
      </div>
    </div>
  )
}

function DistributionBar({
  label,
  percent,
  tone,
  emphasize,
}: {
  label: string
  percent: number
  tone: 'scatter' | 'wild' | 'regular'
  emphasize?: boolean
}) {
  const fillClass =
    tone === 'scatter'
      ? 'strip-marketing__bar-fill--scatter'
      : tone === 'wild'
        ? 'strip-marketing__bar-fill--wild'
        : 'strip-marketing__bar-fill--regular'

  return (
    <div className={cn('strip-marketing__bar', emphasize && 'strip-marketing__bar--emphasize')}>
      <div className="strip-marketing__bar-head">
        <span>{label}</span>
        <span className="strip-marketing__bar-value tabular-nums">{percent.toFixed(1)}%</span>
      </div>
      <div className="strip-marketing__bar-track">
        <div
          className={cn('strip-marketing__bar-fill', fillClass)}
          style={{ width: `${Math.min(percent * 4.5, 100)}%` }}
        />
      </div>
    </div>
  )
}
