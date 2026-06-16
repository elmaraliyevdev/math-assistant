# Math Assistant — User Guide

Platform guide for organizations, games, simulations, analytics, collaboration, and notifications.

## Getting started

### Create an account

1. Open the platform URL and click **Register**.
2. Enter your name, email, and password (minimum 8 characters).
3. You are signed in automatically; a default workspace organization is created.

### Sign in

Use **Sign in** with your email and password. Sessions refresh automatically; sign out from the sidebar (desktop) or navigation menu (mobile) when using a shared machine.

### Onboarding wizard

First-time users are guided through **Getting started** (`/onboarding`):

1. **Welcome** — overview and optional link to game templates.
2. **Organization** — create or confirm your workspace.
3. **Game** — create your first game.
4. **Version** — paste canonical JSON or import from a template.
5. **Simulation** — run a 100,000-spin calibration simulation.
6. **Results** — view status and open the simulation detail page.

A progress bar shows your current step and estimated time remaining. You can also browse **Templates** at any time to start from a pre-built game model.

## Navigation

On desktop, use the left sidebar. On mobile and tablet, open the **hamburger menu** in the header to access all routes: Dashboard, Games, Templates, Simulations, Mathematics, Assistant, Audit, Organization, and Settings.

## Organizations

Organizations are workspaces that own games and simulations.

- **Default workspace** — created at registration.
- **Create organization** — Organization → enter name and slug → **Create organization**.
- **Switch workspace** — use the organization switcher in the header.
- **Members** — owners/admins can invite members and assign roles (owner, admin, developer, viewer).

## Games

Games are containers for mathematical models.

1. Go to **Games** → **Create game** (empty state CTA when no games exist).
2. Enter a name and optional description.
3. Open the game detail page to manage versions.

## Templates

**Templates** provides starter canonical JSON models you can preview and use when creating games or uploading versions. Browse templates from the sidebar or during onboarding.

## Versions

Each game version stores a canonical JSON model validated against the engine.

1. On a game detail page, click **Upload new version**.
2. Paste canonical JSON or upload a `.json` file.
3. Confirm engine version (default matches deployed runtime).
4. Click **Create version** — validation runs before save.
5. If validation fails, review findings in the dialog and fix the JSON.

View version metadata, content hash, and canonical JSON from the version detail page. Export canonical JSON via **Export JSON**.

## Simulations

Simulations execute Monte Carlo runs against a game version.

### Create a simulation

1. Go to **Simulations** → **Create simulation**.
2. Select game and version.
3. Set spin count, bet size (minor units), optional master seed, event log mode.
4. Click **Start simulation**.

Hover the help icons next to fields such as **Bet (minor units)** and **Master seed** for glossary definitions. Simulation results dashboards include tooltips for RTP, hit frequency, volatility, confidence intervals, and exposure cap.

### Monitor progress

The simulation detail page polls progress until completion. Cancel pending/running simulations if needed.

### Compare simulations

Go to **Simulations** → **Compare simulations** (or open `/simulations/compare`). Select two to five completed simulations to compare RTP, volatility, and exposure side by side. Save comparison sessions locally for quick recall.

### Results & analytics

When completed, view:

- **RTP** — return to player and confidence intervals
- **Volatility** — distribution metrics and hit frequency
- **Exposure** — truncation and capped vs uncapped RTP
- **Feature frequencies** — bonus/feature trigger rates
- **Jackpot frequencies** — tier hit rates
- **Win distribution** — bucketed outcomes

Export results as CSV, JSON, or PDF from the simulation detail page.

## Review workflow

Simulations can enter an approval workflow (draft → under review → approved / changes requested).

- Open a simulation’s **Review** tab to see workflow status, comments, and decisions.
- Admins and owners can approve, reject (with required reason), or request changes.
- The dashboard **My pending reviews** widget lists simulations awaiting your decision.
- Notifications link directly to the review page for the relevant simulation.

## Mathematics Assistant

The **Assistant** page provides grounded answers about simulation results, game versions, and comparisons. Select a mode (simulation analysis, comparison, or game version design), choose context, and ask questions. Responses include citations to stored mathematics artifacts.

If you have no games or completed simulations yet, empty-state prompts guide you to create them first.

## Mathematics workbench

The **Mathematics** page provides calibration dashboards, comparison workbenches, and tuning recommendations for completed simulations linked from version and simulation detail views.

## Notifications

Click the bell icon in the header to open the notification center.

- Simulation completed / failed
- Review workflow updates
- Validation failures (when enabled)
- Organization invitations

Filter by type, mark individual notifications read, or **Mark all read**. Control preferences under **Settings → Notifications**.

## Settings

**Settings** page:

- **Profile** — update display name
- **Password** — change password (requires current password)
- **Appearance** — light/dark theme
- **Notifications** — toggle event categories

## Audit log

**Audit** shows platform activity: logins, game/version changes, simulations, membership changes. Filter by user, action, or date range.

## Dashboard

The dashboard summarizes total/active simulations, average RTP, recent activity, pending reviews, and notifications. Organization owners also see system metrics cards when Prometheus is reachable.

## Tips

- Start with smaller spin counts (e.g. 1,000) to validate a version before large runs.
- Keep canonical JSON under version control; content hash detects duplicates.
- Use organizations to separate client projects or teams.
- Use glossary tooltips (help icons) on metrics and form fields when terminology is unfamiliar.
