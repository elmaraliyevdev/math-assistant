# Domain setup — mathstudio.app

Use this layout when the **marketing landing** is on Vercel and the **product app** runs on Hetzner.

| Host | Serves | Platform |
|------|--------|----------|
| `mathstudio.app` | Landing page | Vercel |
| `www.mathstudio.app` | Redirect or landing | Vercel |
| `app.mathstudio.app` | MathStudio application (SPA + `/api`) | Hetzner |

The app must **not** share the apex domain with the landing page — both need `/` on different stacks.

---

## 1. Dynadot DNS

In Dynadot → **mathstudio.app** → DNS / Name Servers:

### Landing (Vercel)

| Type | Host | Value |
|------|------|-------|
| `A` | `@` | `76.76.21.21` |
| `CNAME` | `www` | `cname.vercel-dns.com` |

(Or use the exact records Vercel shows in **Project → Settings → Domains**.)

### Application (Hetzner)

| Type | Host | Value |
|------|------|-------|
| `A` | `app` | `<YOUR_HETZNER_SERVER_IP>` |

Replace `<YOUR_HETZNER_SERVER_IP>` with the public IPv4 of your Hetzner Cloud server.

DNS can take up to an hour to propagate (often a few minutes).

---

## 2. Vercel (landing)

1. Project → **Settings → Domains** → add `mathstudio.app` and `www.mathstudio.app`
2. Confirm Dynadot records match Vercel’s instructions
3. Optional env on Vercel:
   - `NEXT_PUBLIC_APP_URL=https://app.mathstudio.app` (links to the product)

---

## 3. Hetzner (application)

Follow [HETZNER.md](./HETZNER.md) to install Docker and deploy the stack.

### Environment

On the server, edit `deploy/mvp.env` (or a private `.env.mvp`):

```bash
API_JWT_SECRET_KEY=<openssl rand -hex 32>
POSTGRES_PASSWORD=<strong password>
API_FRONTEND_URL=https://app.mathstudio.app
API_ENABLE_HSTS=true
VITE_SITE_URL=https://app.mathstudio.app
VITE_API_BASE_URL=/api
```

Deploy:

```bash
docker compose \
  -f docker-compose.prod.yml \
  --env-file deploy/mvp.env \
  --profile mvp \
  up -d --build
```

### HTTPS (Caddy)

`/etc/caddy/Caddyfile`:

```caddy
app.mathstudio.app {
    reverse_proxy localhost:8080
}
```

```bash
systemctl reload caddy
```

Verify:

```bash
curl -sf https://app.mathstudio.app/api/health
curl -sf https://app.mathstudio.app/api/health/ready
```

---

## 4. Update application code on the server

SSH into Hetzner:

```bash
ssh root@<YOUR_HETZNER_SERVER_IP>
cd math-assistant
./scripts/server-update.sh
```

Or manually:

```bash
git pull
docker compose -f docker-compose.prod.yml --env-file deploy/mvp.env --profile mvp up -d --build
```

Migrations run automatically when the API container starts.

---

## 5. Checklist

- [ ] Dynadot: `@` → Vercel, `app` → Hetzner IP
- [ ] Vercel: `mathstudio.app` verified
- [ ] Hetzner: firewall allows 22, 80, 443 only
- [ ] Caddy: TLS for `app.mathstudio.app`
- [ ] `API_FRONTEND_URL` and `VITE_SITE_URL` set to `https://app.mathstudio.app`
- [ ] `curl https://app.mathstudio.app/api/health` returns OK
- [ ] Login / register works in the browser
- [ ] Password-reset emails link to `https://app.mathstudio.app/...` (when SMTP is enabled)

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Landing works, app does not resolve | Check Dynadot `app` A record points to Hetzner IP |
| App loads but API 502 | `docker compose ... ps` — is `api` healthy? Check logs |
| SSL error on app | Caddy running? Port 443 open? DNS propagated? |
| Email links go to localhost | Set `API_FRONTEND_URL` and redeploy API |
| Wrong canonical URL in app | Rebuild web image with `VITE_SITE_URL` |

See also: [HETZNER.md](./HETZNER.md), [DEPLOYMENT_GUIDE.md](../DEPLOYMENT_GUIDE.md).
