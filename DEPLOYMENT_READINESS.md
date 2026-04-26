# Deployment Readiness

**Last updated**: April 27, 2026

---

## Status: ✅ Ready to deploy (with one required action)

---

## Required before production

**Change `JWT_SECRET`** in `backend/.env` — the default value is insecure:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```
Then set `JWT_SECRET=<output>` in your `.env`.

---

## Quick start (development)

```bash
# Terminal 1 — backend
cd backend
python run.py

# Terminal 2 — frontend
cd frontend
npm run dev
```

Frontend: http://localhost:3000  
Backend health: http://localhost:5000/api/health

---

## Docker (production)

```bash
docker-compose up -d
docker-compose logs -f
```

Frontend served at **http://localhost:3000** via nginx.  
API proxied from nginx → backend container automatically.

---

## Known limitations

| Item | Notes |
|------|-------|
| SQLite | Fine for dev/demo. Use PostgreSQL for production (`DATABASE_URL=postgresql://...`) |
| JWT_SECRET | **Must change** before real users |
| API keys in `.env` | `.env` is gitignored — never commit it |
| No HTTPS | Add a reverse proxy (nginx + certbot, or Cloudflare) for production |
| Polling, not WebSocket | Dashboard refreshes every 10s — acceptable for current scale |

---

## Checklist

- [x] All routes registered and tested
- [x] Auth + rate limiting in place
- [x] CORS configured
- [x] Docker multi-stage build (nginx serves built frontend)
- [x] nginx proxies `/api` to backend — no CORS issues in Docker
- [x] gunicorn timeout set to 180s (covers full agent pipeline)
- [x] TPO dashboard 404-on-no-report handled gracefully (no false error banner)
- [x] `.env` gitignored
- [x] `.env.example` up to date
- [ ] **JWT_SECRET changed** (required for production)
- [ ] PostgreSQL configured (recommended for production)
- [ ] HTTPS / reverse proxy configured (required for production)
