# Landing demo visual QA checklist (PR 4)

Compare each embedded demo against the corresponding screen in `packages/web` (dark mode). Target: **95–99% visual similarity**.

## Shared chrome (all demos)

| Check | App (`AppSidebar` + page header) | Landing (`PreviewAppChrome` + `DemoFrame`) | Status |
| --- | --- | --- | --- |
| Sidebar width | `w-60` (240px) | `w-60` | Match |
| Logo height | ~24px in sidebar | `h-6` (24px) | Match |
| Nav item padding | `px-3 py-2`, `text-sm` | Same classes | Match |
| Header height | App header ~48–56px | `h-12` chrome header | Close |
| Border radius (frame) | N/A (full app) | `rounded-lg` browser frame | Intentional |
| Content scale | 1:1 | `demo-frame.css` scale ~0.76–0.78 | Intentional (fit viewport) |

## Reel Studio

| Check | App (`DesignStudioLayout`) | Landing (`ReelStudioDemo`) | Status |
| --- | --- | --- | --- |
| Layout component | Full design studio (toolbar, inspectors, canvas) | `ReelStudioLayout` (editor grid only) | **Gap** — simplified view |
| Reel grid / symbols | Real `ReelEditor` | Same components + providers | Match |
| Toolbar / save actions | Present | Omitted in `ReelStudioLayout` | **Gap** |
| JSON preview | Available | `JsonPreviewDrawer` (static in preview) | Match |

## Simulation

| Check | App (simulation detail page) | Landing (`SimulationDemo`) | Status |
| --- | --- | --- | --- |
| Hero / status | `SimulationDetailHero` | Same (`previewMode`) | Match |
| Health metrics | `SimulationHealthSummary` | Same | Match |
| Charts / shard table | Full detail tabs | Not shown | **Gap** — hero + summary only |
| Narrative | Crown Quest v3.2, 10M spins, 95.96% RTP | Same demo data | Match |

## Mathematics

| Check | App (calibration workbench) | Landing (`MathematicsDemo`) | Status |
| --- | --- | --- | --- |
| Dashboard | `CalibrationDashboard` | Same (props-only data) | Match |
| Wizard / run actions | Interactive | Hidden via `previewMode` + `pointer-events-none` | Intentional |
| Compact scale | Full page | `demo-calibration` CSS tweaks | Minor density diff |

## Certification

| Check | App (`SimulationReviewPage`) | Landing (`CertificationDemo`) | Status |
| --- | --- | --- | --- |
| Workflow cards | Live API hooks | Presentation views + demo data | Match (static) |
| Comments | `CommentsPanel` (mutations) | `CommentsPanelView` | Match (read-only) |
| Activity | API-driven timeline | `ActivityTimelineView` | Match (read-only) |
| Readiness panel | `CertificationReadinessPanel` | Same | Match |

## Intentional differences (do not “fix” in PR 4)

1. **Browser frame** — border, shadow, and viewport scaling exist only on the landing.
2. **Preview mode** — `pointer-events-none`, no navigation, no saves, no dialogs, no downloads.
3. **Static chrome** — `PreviewAppChrome` mirrors sidebar/header visually but does not use TanStack Router or live breadcrumbs.
4. **Reduced depth** — Reel Studio and Simulation demos show representative regions, not every tab/panel from full pages.
5. **Content scale** — `demo-frame.css` scales content to fit walkthrough sections.

## Narrative consistency (Crown Quest v3.2)

- Game: **Crown Quest**
- Version: **3.2** (`version-crown-quest-v3`)
- Simulation: **sim-crown-quest-4821**, 10M spins, RTP **95.96%**, σ **4.18**
- Certification: same simulation, workflow, and calibration readiness data in `packages/demo/src/data/`

## Regression watchlist

When `packages/web` UI changes, verify:

- [ ] `presentation.ts` exports still cover landing imports
- [ ] `math-studio-lp` webpack + `tsconfig` paths resolve new `@/` modules
- [ ] `Preview*Provider` stacks include any new required React context
- [ ] `npm run build` in `math-studio-lp` passes
