# Hetzner Deployment — Math Assistant MVP

This guide deploys Math Assistant on a single Hetzner Cloud server using the **MVP profile**: one API container, one Celery simulation worker, PostgreSQL, Redis, and the web UI.

## Recommended server

| Tier | Hetzner type | vCPU | RAM | Notes |
|------|--------------|------|-----|-------|
| MVP (default) | **CX33** | 4 | 8 GB | Comfortable for ≤10M-spin simulations, 2 concurrent jobs |
| Minimum | **CX23** | 2 | 4 GB | Light usage only; monitor memory during large runs |
| Enterprise | **CX43+** | 8+ | 16+ GB | Use `--profile enterprise` and scale workers |

Choose a location close to your users (e.g. `nbg1` Nuremberg, `hel1` Helsinki).

## 1. Provision the server

1. Create a Hetzner Cloud project and add an **Ubuntu 24.04** server.
2. Add your SSH key at creation time.
3. Attach a **firewall** allowing:
   - TCP **22** (SSH) — restrict to your IP
   - TCP **80** / **443** (HTTP/HTTPS) — public
   - Do **not** expose PostgreSQL (5432) or Redis (6379) publicly.

## 2. Install Docker

SSH into the server:

```bash
ssh root@YOUR_SERVER_IP
```

Install Docker Engine and Compose plugin:

```bash
apt-get update
apt-get install -y ca-certificates curl
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] \
  https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo ${VERSION_CODENAME}) stable" \
  > /etc/apt/sources.list.d/docker.list

apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

## 3. Deploy the application

```bash
git clone https://github.com/YOUR_ORG/math-assistant.git
cd math-assistant

# Set secrets (required)
export API_JWT_SECRET_KEY="$(openssl rand -hex 32)"
export POSTGRES_PASSWORD="$(openssl rand -hex 24)"

# Optional: copy and edit deploy/mvp.env
cp deploy/mvp.env .env.mvp
# Edit API_JWT_SECRET_KEY and POSTGRES_PASSWORD in .env.mvp

docker compose \
  -f docker-compose.prod.yml \
  --env-file deploy/mvp.env \
  --profile mvp \
  up -d --build
```

MVP safeguards (enforced by the API, configured via env):

| Setting | MVP value |
|---------|-----------|
| `API_DEPLOYMENT_MODE` | `mvp` |
| `API_SIMULATION_WORKER_COUNT` | `1` |
| Celery workers | `1` (`--concurrency=1`) |
| `API_MAX_ACTIVE_SIMULATIONS` | `2` |
| `API_MAX_SIMULATION_SPIN_COUNT` | `10,000,000` |

Verify services:

```bash
docker compose -f docker-compose.prod.yml --profile mvp ps
curl -s http://localhost:8080/api/health
curl -s http://localhost:8080/api/engine/version | jq '.maxRecommendedSpinCount'
```

## 4. HTTPS with Caddy (recommended)

Install Caddy on the host and reverse-proxy to the web container:

```bash
apt-get install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list
apt-get update && apt-get install -y caddy
```

`/etc/caddy/Caddyfile`:

```caddy
math.example.com {
    reverse_proxy localhost:8080
}
```

```bash
systemctl reload caddy
```

Set `API_ENABLE_HSTS=true` in your env file once HTTPS is working.

## 5. Backups

Hetzner volumes or object storage can hold PostgreSQL dumps:

```bash
docker compose -f docker-compose.prod.yml --profile mvp exec postgres \
  pg_dump -U postgres math_assistant > backups/math_assistant-$(date +%F).sql
```

Automate with a cron job and off-site sync (Hetzner Storage Box or S3-compatible storage).

## 6. Upgrading

```bash
cd math-assistant
git pull
docker compose -f docker-compose.prod.yml --env-file deploy/mvp.env --profile mvp up -d --build
```

Migrations run automatically when the API container starts.

## 7. Scaling to enterprise

When you outgrow the MVP limits, switch profiles without changing application code:

```bash
docker compose -f docker-compose.prod.yml \
  --env-file deploy/enterprise.env \
  --profile enterprise \
  up -d --build --scale simulation-worker=4
```

Enterprise removes the 2-simulation concurrency cap and raises spin limits via `deploy/enterprise.env`.

For worker scaling, Redis sizing, and queue monitoring, see **[CELERY_WORKER_SCALING.md](../operations/CELERY_WORKER_SCALING.md)**.

## Troubleshooting

| Symptom | Check |
|---------|-------|
| Simulations stay `pending` | `docker compose ... logs simulation-worker` — Redis reachable? |
| `429 ACTIVE_SIMULATION_LIMIT_EXCEEDED` | MVP allows 2 concurrent runs; wait or cancel a job |
| `400 SIMULATION_SPIN_COUNT_EXCEEDED` | MVP caps at 10M spins per simulation |
| Out of memory | Reduce spin count, upgrade to CX33/CX43, or add swap temporarily |

See also: [DEPLOYMENT_GUIDE.md](../DEPLOYMENT_GUIDE.md), [OPERATIONS_RUNBOOK.md](../OPERATIONS_RUNBOOK.md).
