# Math Assistant

A mathematics platform for slot game design: upload and validate canonical game JSON, run simulations, analyze RTP and certification readiness, and visually edit reel strips in **Reel Studio**.

| Layer | Stack |
|-------|--------|
| Web UI | React 19, TypeScript, Vite, TanStack Router/Query |
| API | FastAPI, PostgreSQL, SQLAlchemy, Alembic |
| Engine | `runtime-core@1.8.0` (frozen simulation & validation core) |

---

## Prerequisites

Choose one path below.

**Docker (recommended for first run)**

- [Docker](https://docs.docker.com/get-docker/) 24+
- [Docker Compose](https://docs.docker.com/compose/) v2

**Local development (API + web on your machine)**

- Python **3.13+** with [uv](https://docs.astral.sh/uv/)
- Node.js **20+** and npm
- PostgreSQL **16** (running locally on port `5432`)

---

## Quick start (Docker)

From the repository root:

```bash
docker compose up -d --build
```

This starts:

| Service | URL | Notes |
|---------|-----|--------|
| Web UI | http://localhost:5173 | React app |
| API | http://localhost:8000 | FastAPI backend |
| PostgreSQL | `localhost:5433` | User/password/db: `postgres` / `postgres` / `math_assistant` (host port 5433 avoids conflict with local Postgres on 5432) |

Database migrations run automatically when the API container starts.

Open http://localhost:5173, register an account, and complete onboarding.

### Simulations with Redis + Celery (MVP profile)

The default `docker compose up` runs simulations **in-process** inside the API. For the distributed worker queue (closer to production):

```bash
export API_JWT_SECRET_KEY="$(openssl rand -hex 32)"
docker compose --env-file deploy/mvp.env --profile mvp up -d --build
```

This also starts **Redis** and a **simulation-worker** container.

### Production-style deployment

```bash
export API_JWT_SECRET_KEY="$(openssl rand -hex 32)"
docker compose -f docker-compose.prod.yml --env-file deploy/mvp.env --profile mvp up -d --build
```

See [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) for enterprise profiles, Hetzner setup, and security recommendations.

---

## Local development (without Docker)

### 1. Start PostgreSQL

Create the database (once):

```sql
CREATE DATABASE math_assistant;
```

Or use any existing PostgreSQL 16 instance reachable at `localhost:5432`.

### 2. API

```bash
cd packages/api
cp .env.example .env   # edit API_DATABASE_URL if needed
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API listens on http://localhost:8000.

Useful checks:

- Health: http://localhost:8000/health
- Engine version: http://localhost:8000/engine/version
- OpenAPI docs: http://localhost:8000/docs

### 3. Web

In a second terminal:

```bash
cd packages/web
npm install
npm run dev
```

The Vite dev server runs at http://localhost:5173 and proxies `/api` requests to `http://127.0.0.1:8000`.

Optional: set `VITE_API_BASE_URL` if the API is on a different host (default is `/api`).

---

## Using the app

1. **Register / log in** at http://localhost:5173
2. **Create an organization** (onboarding flow)
3. **Games** — create a game and upload a canonical JSON version (templates are available under **Templates**)
4. **Reel Studio** — open a version and click **Open Reel Studio** to edit reel strips visually, or use the sidebar **Reel Studio** entry
5. **Simulations** — run spins against a game version and review analytics
6. **Mathematics** — theoretical RTP, calibration, and certification reports

---

## Tests

### API

```bash
cd packages/api
uv run pytest -v
```

### Web

```bash
cd packages/web
npm test
npm run test:coverage:reel-studio   # Reel Studio module coverage
```

### End-to-end (full Docker stack)

```bash
cd e2e
npm install
npm run install:browsers
npm test
```

See [e2e/README.md](e2e/README.md).

---

## Project layout

```
math-assistant/
├── packages/
│   ├── api/            # FastAPI platform (auth, games, simulations, reel-studio merge API)
│   ├── web/            # React frontend (includes features/reel-studio)
│   ├── runtime_core/   # Frozen game engine & validator
│   └── game-schema/    # Canonical JSON JSON Schema
├── deploy/             # Compose env files (mvp.env, enterprise.env)
├── docs/               # Architecture, deployment, operations
├── docker-compose.yml
└── docker-compose.prod.yml
```

---

## Configuration reference

| Variable | Package | Description |
|----------|---------|-------------|
| `API_DATABASE_URL` | API | PostgreSQL URL (`postgresql+asyncpg://...`) |
| `API_JWT_SECRET_KEY` | API | JWT signing secret (required in production) |
| `API_SIMULATION_EXECUTION_BACKEND` | API | `inprocess` or `distributed` |
| `VITE_API_BASE_URL` | Web | API base URL (default `/api`) |

Full lists: [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md), [packages/api/.env.example](packages/api/.env.example).

---

## Documentation

| Topic | Location |
|-------|----------|
| Deployment & profiles | [docs/DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) |
| API specification | [docs/API_SPECIFICATION.md](docs/API_SPECIFICATION.md) |
| Operations & migrations | [docs/OPERATIONS_RUNBOOK.md](docs/OPERATIONS_RUNBOOK.md) |
| Canonical game JSON | [docs/CANONICAL_GAME_SCHEMA_V1.md](docs/CANONICAL_GAME_SCHEMA_V1.md) |
| Platform architecture | [docs/PLATFORM_ARCHITECTURE.md](docs/PLATFORM_ARCHITECTURE.md) |

---

## Troubleshooting

**Web build or API errors after `git pull`**

```bash
cd packages/web && npm install && npm run build
cd packages/api && uv sync
```

**`docker compose` fails without env file (MVP/enterprise profile)**

Always pass the env file when using profiles:

```bash
docker compose --env-file deploy/mvp.env --profile mvp up -d --build
```

**Database connection refused (local dev)**

Ensure PostgreSQL is running and `API_DATABASE_URL` in `packages/api/.env` matches your instance. Run migrations:

```bash
cd packages/api && uv run alembic upgrade head
```

**Port already in use**

Stop conflicting services or change ports in `docker-compose.yml` / uvicorn / Vite config.

---

## License

See repository license terms if applicable.
