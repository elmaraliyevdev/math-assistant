# Changelog

All notable changes to the Math Assistant platform are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [1.0.0] — 2026-06-15

### Platform freeze

First production-ready release of the Math Assistant MVP platform. **No engine behavior changes** in this release; `runtime-core@1.8.0` remains frozen per [docs/ENGINE_RELEASE_v1.0.md](docs/ENGINE_RELEASE_v1.0.md).

### Added — Platform (Phases 11–14)

- **Authentication & organizations** — register, login, JWT refresh rotation, org membership and roles
- **Games & versions** — CRUD, canonical JSON upload, validation workflow, content hashing
- **Simulations** — async worker queue, progress polling, cancel, results API
- **Analytics UI** — RTP, volatility, exposure, feature/jackpot frequencies, win distribution charts
- **Notifications** — persisted notification center with preferences
- **Audit log** — platform activity tracking and filters
- **User settings** — profile, password, theme, notification preferences
- **Exports** — simulation results (CSV/JSON/PDF), game version canonical JSON
- **Dashboard** — summary widgets, recent activity, metrics overview
- **Observability** — Prometheus `/metrics`, Sentry integration, Grafana dashboards
- **Security** — security headers, auth rate limiting, brute-force lockout, body size limits, refresh token reuse detection
- **Operations** — production Docker Compose, operations runbook, beta checklist, user guide
- **E2E tests** — Playwright critical user journeys

### Packages

| Package | Version |
|---------|---------|
| `runtime-core` (engine) | `runtime-core@1.8.0` |
| `math-assistant-api` | `1.0.0` |
| `@math-assistant/web` | `1.0.0` |

### Documentation

- Deployment guide, operations runbook, user guide, security docs, performance validation, release notes

---

## Engine history (frozen at `runtime-core@1.8.0`)

Engine phases M0–M9 (validation, runtime, simulation, mathematical) completed 2026-06-14. See [docs/ENGINE_RELEASE_v1.0.md](docs/ENGINE_RELEASE_v1.0.md).

[1.0.0]: https://github.com/math-assistant/math-assistant/releases/tag/api%401.0.0
