'use client'

import { Badge } from '@/components/ui/badge'

import { HeroSymbolGraphic } from '../components/HeroSymbolGraphic'
import { useConstraintsPreview } from '../hooks/use-constraints-preview'
import { cn } from '../lib/cn'

import '../styles/constraints-marketing.css'

const VIOLATION_STRIP = ['SCAT', 'LV1', 'SCAT', 'HV1', 'SCAT', 'LV2', 'WILD'] as const

/** Marketing composition: constraint rules + reel violation highlight. */
export function ConstraintsPreview() {
  const { rules, caption, highlightReel, showResolved, summary } = useConstraintsPreview()

  const reelStrip = highlightReel !== undefined ? [...VIOLATION_STRIP] : null

  return (
    <div className="constraints-marketing">
      <div className="constraints-marketing__header">
        <p className="constraints-marketing__caption">{caption}</p>
        <div className="constraints-marketing__badges">
          <Badge variant="secondary" className="constraints-marketing__badge tabular-nums">
            {summary.passes} PASS
          </Badge>
          <Badge
            variant={summary.errors > 0 ? 'danger' : 'success'}
            className={cn(
              'constraints-marketing__badge tabular-nums',
              summary.errors === 0 && showResolved && 'constraints-marketing__badge--pop',
            )}
          >
            {summary.errors > 0 ? `${summary.errors} ERROR` : '0 ERRORS'}
          </Badge>
        </div>
      </div>

      <div className="constraints-marketing__body">
        <ul className="constraints-marketing__rules">
          {rules.map((rule) => (
            <li
              key={rule.id}
              className={cn(
                'constraints-marketing__rule',
                rule.state === 'error' && 'constraints-marketing__rule--error',
                rule.state === 'pass' && showResolved && 'constraints-marketing__rule--resolved',
              )}
            >
              <span
                className={cn(
                  'constraints-marketing__rule-icon',
                  rule.state === 'pass' && 'constraints-marketing__rule-icon--pass',
                  rule.state === 'error' && 'constraints-marketing__rule-icon--error',
                )}
                aria-hidden
              >
                {rule.state === 'error' ? '✕' : '✓'}
              </span>
              <div className="constraints-marketing__rule-copy">
                <span className="constraints-marketing__rule-label">{rule.label}</span>
                <span className="constraints-marketing__rule-detail">{rule.detail}</span>
              </div>
            </li>
          ))}
        </ul>

        {reelStrip ? (
          <aside className="constraints-marketing__focus">
            <p className="constraints-marketing__focus-label">Affected strip</p>
            <p className="constraints-marketing__focus-reel">Reel 3</p>
            <div className="constraints-marketing__focus-strip">
              {reelStrip.map((symbolId, index) => {
                const isScatter = symbolId === 'SCAT'

                return (
                  <div
                    key={`${symbolId}-${index}`}
                    className={cn(
                      'constraints-marketing__focus-slot',
                      isScatter && 'constraints-marketing__focus-slot--violation',
                    )}
                  >
                    <HeroSymbolGraphic symbolId={symbolId} />
                  </div>
                )
              })}
            </div>
            <p className="constraints-marketing__focus-hint">
              3 Scatter symbols — limit is 2
            </p>
          </aside>
        ) : (
          <aside className="constraints-marketing__focus constraints-marketing__focus--clear">
            <p className="constraints-marketing__focus-label">Constraint engine</p>
            <p className="constraints-marketing__focus-clear-title">Live on every edit</p>
            <p className="constraints-marketing__focus-clear-copy">
              Scatter limits, adjacency rules, and symbol inventory — checked before you
              simulate.
            </p>
          </aside>
        )}
      </div>
    </div>
  )
}
