# ⚡ Quick Reference Card

## What Changed?
✅ **Anthropic Claude → Groq + Ollama**
✅ **Expensive API → Free options**
✅ **All features work the same**

---

## Two Ways to Run It

### Option 1: Groq (Fast, Cloud) ⚡
```
Setup: 2 min  |  Speed: Very Fast  |  Cost: Free
```
1. Go to https://console.groq.com (instant signup, no card)
2. Copy your API key
3. `echo AI_PROVIDER=groq > backend\.env`
4. `echo GROQ_API_KEY=your_key >> backend\.env`
5. `cd backend && python wsgi.py`
6. `cd frontend && npm run dev` (new terminal)
7. Open http://localhost:5173

---

### Option 2: Ollama (Local, Offline) 🏠
```
Setup: 15 min  |  Speed: Slower  |  Cost: Free
```
1. Download from https://ollama.ai (2min install)
2. Terminal 1: `ollama pull mistral` then `ollama serve`
3. Terminal 2: `echo AI_PROVIDER=ollama > backend\.env`
4. `cd backend && python wsgi.py`
5. Terminal 3: `cd frontend && npm run dev`
6. Open http://localhost:5173

---

## Files You Need to Edit

Only **one file needs editing**:

### `backend/.env`
```dotenv
# For Groq:
AI_PROVIDER=groq
GROQ_API_KEY=your_api_key_here

# OR for Ollama:
AI_PROVIDER=ollama
OLLAMA_URL=http://localhost:11434
```

---

## Important URLs

| What | URL |
|------|-----|
| **Get Groq Key** | https://console.groq.com |
| **Download Ollama** | https://ollama.ai |
| **Frontend** | http://localhost:5173 |
| **Backend** | http://localhost:5000 |

---

## Commands Cheat Sheet

### Setup (First Time)
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
```

### Run Backend
```bash
cd backend
venv\Scripts\activate
python wsgi.py
```

### Run Frontend
```bash
cd frontend
npm install  # First time only
npm run dev
```

### Start Ollama (if using Ollama)
```bash
ollama pull mistral  # First time only
ollama serve
```

---

## Troubleshooting Fast Track

| Problem | Fix |
|---------|-----|
| API key error | Check .env has GROQ_API_KEY=actual_key_not_placeholder |
| Ollama connection error | Make sure `ollama serve` is running |
| Port 5000 in use | Kill existing Flask: `lsof -ti:5000 \| xargs kill` |
| Module not found | Run `pip install -r requirements.txt` again |
| npm not found | Install Node.js from nodejs.org |

---

## Features Available

✅ Resume-Job Matching (0-100% score)
✅ Skill Gap Analysis
✅ Resume Improvement
✅ Career Field Suggestions
✅ Interview Question Generation
✅ PDF Upload Support

---

## Reading Guide

| If You... | Read This |
|-----------|-----------|
| Want quick start | **START_HERE.md** |
| Using Ollama | **OLLAMA_SETUP.md** |
| Had Anthropic before | **MIGRATION_GUIDE.md** |
| Want all details | **SETUP_GUIDE.md** |
| Just want overview | **README.md** |

---

## Environment Variables Reference

```dotenv
# REQUIRED: Choose one
AI_PROVIDER=groq          # Cloud option (recommended)
AI_PROVIDER=ollama        # Local option

# REQUIRED if using Groq:
GROQ_API_KEY=gsk_...      # From https://console.groq.com

# REQUIRED if using Ollama:
OLLAMA_URL=http://localhost:11434  # Local Ollama server

# Optional (Flask):
FLASK_ENV=development
FLASK_DEBUG=True
PORT=5000
CORS_ORIGINS=*
```

---

## API Endpoints

All 6 endpoints work identically:

| Endpoint | Purpose |
|----------|---------|
| `GET /api/health` | Health check |
| `POST /api/analyze` | Resume analysis |
| `POST /api/improve-resume` | Resume optimization |
| `POST /api/career-fields` | Career suggestions |
| `POST /api/interview-prep` | Interview questions |
| `POST /api/upload-pdf` | PDF upload |

---

## Quick Decision Guide

```
Fast setup needed? → Use GROQ
Want best speed? → Use GROQ
Privacy important? → Use OLLAMA
Offline needed? → Use OLLAMA
Not sure? → Use GROQ
```

---

## Status

✅ Backend complete (supports Groq + Ollama)
✅ Frontend complete (no changes needed)
✅ Documentation complete
✅ Ready to use!

---

**Next Step:** Go to START_HERE.md and follow the 5-minute guide!

---

*Quick Reference v1.0 - January 2026*
