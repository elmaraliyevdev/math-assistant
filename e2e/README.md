# End-to-End Tests (Playwright)

Critical user journey tests against the full Docker stack.

## Prerequisites

- Docker and Docker Compose
- Node.js 22+

## Setup

```bash
cd e2e
npm install
npm run install:browsers
```

## Run tests

Start stack automatically (or reuse running `docker compose up`):

```bash
npm test
```

Environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `E2E_BASE_URL` | `http://localhost:5173` | Web UI base URL |
| `E2E_SKIP_WEBSERVER` | unset | Set to skip docker webServer |

## Covered journeys

- Registration and login
- Organization creation
- Game creation and version upload (with validation)
- Simulation create → monitor → analytics
- Notifications center
- Settings profile update
- Audit log visibility

## CI

```bash
docker compose up -d --build
cd e2e && npm ci && npm run install:browsers && E2E_SKIP_WEBSERVER=1 npm test
```
