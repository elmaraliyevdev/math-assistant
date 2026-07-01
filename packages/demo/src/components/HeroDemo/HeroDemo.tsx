'use client'

import { useHeroWalkthrough } from '../../hooks/use-hero-walkthrough'
import { HeroWalkthroughPreview } from '../../previews/HeroWalkthroughPreview'
import {
  DEMO_HERO_DESIGN_WIDTH,
  DemoScale,
} from '../../shell/DemoScale'

import '../../styles/hero-demo.css'

/** Animated hero reel studio — matches premium marketing reference. */
export function HeroDemo() {
  const walkthrough = useHeroWalkthrough()

  return (
    <DemoScale designWidth={DEMO_HERO_DESIGN_WIDTH}>
      <div className="hero-demo">
        <HeroWalkthroughPreview {...walkthrough} />
      </div>
    </DemoScale>
  )
}
