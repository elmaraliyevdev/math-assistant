# Demo components architecture

This document describes the foundation for sharing **real application UI** on the marketing landing page (`math-studio-lp`) without handcrafted mockups.

## Purpose

Today the repository has two frontends:

| Package | Role | UI source |
|---------|------|-----------|
| `packages/web` | Product application | Real feature components + API |
| `math-studio-lp` | Marketing landing | Handcrafted `components/product/*` mocks |

The goal is a single visual language: landing sections render **demo wrappers** around the same React components and data shapes as the product.

**This PR establishes the foundation only.** Feature-specific demos (Reel Studio, Simulation, etc.) and landing migration are follow-up PRs.

---

## Architecture analysis (current state)

### Duplicated components

| Concern | Landing (`math-studio-lp`) | Application (`packages/web`) |
|---------|---------------------------|------------------------------|
| Logo | Inline SVG placeholder in `components/ui/logo.tsx` | `components/logo.tsx` + synced SVG assets |
| Button / Card / Badge | `components/product/ui.tsx`, `components/ui/button.tsx` | Radix/shadcn `components/ui/*` |
| App chrome | `components/product/app-shell.tsx` | `AppLayout`, `AppSidebar`, `AppHeader` |
| Product previews | `reel-studio-ui.tsx`, `calibration-ui.tsx`, etc. | `features/reel-studio`, `features/mathematics`, … |
| `cn()` utility | `lib/utils.ts` | `lib/utils.ts` |

### Duplicated design tokens

Both apps use Tailwind v4 with similar token names (`--background`, `--primary`, …) but **different values**:

- Landing: dark-only, hue ~264, radius `0.625rem`, Geist fonts
- Application: light + dark, hue ~250, radius `0.75rem`

Future PRs should unify tokens before swapping landing mocks for real components.

### Branding assets (before this PR)

Canonical SVGs lived at the **repository root** and were copied into `packages/web` by `scripts/sync-brand-assets.mjs`. The landing page did not consume them.

---

## New packages

### `@math-assistant/brand` (`packages/brand`)

**Single source of truth for branding assets and metadata.**

```
packages/brand/
├── assets/           # logo.svg, logo-white.svg, icons, favicon.svg
├── scripts/
│   └── sync-assets.mjs   # copies assets → web + landing public folders
└── src/
    ├── brand.ts      # BRAND metadata, asset filename helpers
    ├── Logo.tsx      # framework-agnostic Logo (pass resolved `src`)
    └── index.ts
```

Run sync:

```bash
node packages/brand/scripts/sync-assets.mjs
# or (unchanged for web dev/build):
cd packages/web && npm run sync:brand
```

**Note:** `logo-black.svg` does not exist in the repo. The dark icon mark is `black-logo-icon.svg`.

`packages/web` and `math-studio-lp` still use their existing Logo components in this PR. Migrate them to `@math-assistant/brand` in a follow-up.

### `@math-assistant/demo` (`packages/demo`)

**Typed demo data + generic UI building blocks + animation hooks.**

```
packages/demo/
├── src/
│   ├── data/           # fixtures typed against web API models
│   ├── components/     # DemoFrame, DemoSection, DemoCard
│   ├── hooks/          # useDemoTicker, useDemoAnimation, useDemoClock
│   ├── lib/cn.ts
│   └── index.ts
└── tests/
```

Types are imported from `packages/web` via TypeScript path aliases (`@web/types/*`, `@web/services/*`). No runtime dependency on the web app.

---

## Demo data

All fixtures use **existing API interfaces** from `packages/web/src/types/api.ts` and `packages/web/src/services/dashboard.ts`.

| Module | Types | Narrative |
|--------|-------|-----------|
| `games.ts` | `Game`, `GameVersionSummary` | Crown Quest v3 + sample catalog |
| `simulation.ts` | `SimulationResults` | 10M-spin certified-style results |
| `mathematics.ts` | `TheoreticalAnalysisResponse`, `CalibrateResponse` | RTP aligned within tolerance |
| `certification.ts` | `CertificationReportResponse` | Export-ready package |
| `organization.ts` | `Organization`, `OrganizationMember` | MathStudio Labs team |
| `workspace.ts` | `DashboardSummary` | Dashboard activity feed |

Shared IDs live in `data/constants.ts` so demos stay consistent.

When adding data, prefer extending test fixtures (e.g. `packages/web/tests/fixtures/certified-results.ts`) rather than inventing new shapes.

---

## Demo infrastructure components

### `DemoFrame`

Product chrome wrapper (header, optional breadcrumb/toolbar, brand slot). Use for “screenshot replacement” regions.

```tsx
import { Logo } from '@math-assistant/brand'
import { DemoFrame } from '@math-assistant/demo'

<DemoFrame
  brand={<Logo src="/logo-white.svg" theme="dark" />}
  breadcrumb="Reel Studio / Crown Quest"
  inert
>
  {/* future ReelStudioDemo */}
</DemoFrame>
```

### `DemoSection`

Landing section headings (eyebrow, title, description).

### `DemoCard`

Generic bordered card using application token class names (`border-border`, `bg-card`, …). Consumers must include compatible Tailwind/CSS variables.

---

## Animation hooks

| Hook | Purpose |
|------|---------|
| `useDemoTicker` | Animate numbers (spin count, RTP) without APIs |
| `useDemoAnimation` | Step through named phases (hero loops) |
| `useDemoClock` | Relative timestamps for activity feeds |

All hooks are client-only, have no network side effects, and are safe for static landing previews.

---

## How landing should consume demos (future PRs)

1. Add npm workspaces (not in this PR) linking `math-studio-lp` → `@math-assistant/demo`.
2. Configure Next.js `transpilePackages` for `@math-assistant/demo` and `@math-assistant/brand`.
3. Import shared Tailwind tokens from the application (or wrap demos in a `.dark` container with aligned CSS variables).
4. Replace each `components/product/*` mock with a feature demo component.
5. Pass `inert` / `pointer-events-none` on showcase frames.

Example target (not implemented yet):

```tsx
// math-studio-lp — future
import { MathematicsDemo } from '@math-assistant/demo/mathematics'

<MathematicsSection>
  <MathematicsDemo />
</MathematicsSection>
```

---

## Guidelines for future demo components

### Do

- Compose **real** feature components from `packages/web`
- Accept `previewMode` / `readOnly` props (to be added in feature code)
- Use fixtures from `packages/demo/src/data`
- Wrap with `DemoFrame` for consistent chrome
- Keep demos free of API calls, auth, WebSocket, and mutations
- Tree-shake: export feature demos from dedicated entry points

### Do not

- Add PNG screenshots or static images of the product UI
- Duplicate API interfaces in the demo package
- Import `app/router.tsx`, axios clients, or Zustand stores into demos
- Copy/paste shadcn primitives into `math-studio-lp`

### Adding a new landing section (checklist)

1. Add typed data in `packages/demo/src/data/<feature>.ts`
2. Create `packages/demo/src/components/<Feature>Demo/` using real web components
3. Export from `packages/demo/src/index.ts`
4. Swap the landing section import
5. Document the demo in this file

---

## Readonly preview mode (planned)

Not implemented in this PR. Future feature demos will need props such as:

```tsx
<ReelStudioProvider initialDocument={doc} readOnly>
  <DesignStudioLayout previewMode … />
</ReelStudioProvider>
```

Until then, infrastructure components (`DemoFrame`, hooks, data) are ready for composition.

---

## PR 2 — Mathematics demo (completed)

The landing **Mathematics** section renders `<MathematicsDemo />`, which composes the real
`CalibrationDashboard` from `packages/web` with `demoCalibrateResponse` fixtures.

### Integration without workspaces

`math-studio-lp/next.config.ts` maps:

- `@` → `packages/web/src` (application components only; not the router)
- `@math-assistant/demo` → `packages/demo/src`
- `@math-assistant/brand` → `packages/brand/src`

Demo regions import `packages/demo/src/styles/product-demo.css` for application-aligned dark tokens.

### Components still needing decoupling (before Reel Studio demo)

| Area | Blocker | Suggested approach |
|------|---------|-------------------|
| Reel Studio editor | `ReelStudioProvider`, DnD, optimizer/generator contexts | `readOnly` providers + slim `ReelStudioDemoShell` |
| Simulations | Detail pages use React Query hooks | Props-only chart/dashboard components (like `RTPDashboard`) |
| Certification | `CertificationReportViewer` has download actions | `previewMode` to hide actions on landing |
| App chrome | `AppLayout` + TanStack Router | Continue using `DemoFrame` |
| Design tokens | Landing vs app hue/radius differ | Expand `product-demo.css` or unify global tokens |

### Webpack alias strategy (no workspaces)

Landing keeps `@/*` for its own source. Application modules used by demos resolve through
**granular aliases** in `math-studio-lp/next.config.mjs` (e.g. `@/components/ui/badge` →
`packages/web`, while `@/components/ui/button` stays on the landing tree).

Production builds use `next build --webpack` because Turbopack cannot yet resolve monorepo
aliases reliably.

### Types without API coupling

`DashboardSummary` and related interfaces live in `packages/web/src/services/dashboard-types.ts`
so demo fixtures can import types without pulling `dashboardApi` / axios into the landing typecheck.

---

## Related paths

| Path | Description |
|------|-------------|
| `packages/brand/` | Branding assets + Logo |
| `packages/demo/` | Demo data + infrastructure |
| `packages/web/` | Product application |
| `math-studio-lp/` | Marketing landing (not migrated yet) |
| `packages/web/scripts/sync-brand-assets.mjs` | Delegates to brand sync script |

---

## Verification

```bash
# Sync branding to web + landing public folders
node packages/brand/scripts/sync-assets.mjs

# Demo package tests
cd packages/demo && npm install && npm test

# Ensure web build unchanged
cd packages/web && npm run build
```
