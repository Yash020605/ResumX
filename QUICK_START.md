# 🚀 Quick Start Guide

Get ResuMX up and running in 5 minutes!

---

## ⚡ Fastest Way to Start

### Windows
```bash
start-dev.bat
```

### Linux/Mac
```bash
chmod +x start-dev.sh
./start-dev.sh
```

This will:
1. ✅ Create Python virtual environment (if needed)
2. ✅ Install backend dependencies
3. ✅ Start Flask backend on port 5000
4. ✅ Install frontend dependencies (if needed)
5. ✅ Start Vite frontend on port 3000

**Then open**: http://localhost:3000

---

## 🔧 Manual Start (If Scripts Don't Work)

### Step 1: Start Backend

```bash
# Navigate to backend
cd backend

# Create virtual environment (first time only)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies (first time only)
pip install -r requirements.txt

# Start server
python run.py
```

Backend will run on: http://localhost:5000

### Step 2: Start Frontend (New Terminal)

```bash
# Navigate to frontend
cd frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

Frontend will run on: http://localhost:3000

---

## 🐳 Docker Start (Alternative)

```bash
docker-compose up -d
```

This starts both backend and frontend in containers.

---

## ✅ Verify It's Working

### Check Backend
```bash
curl http://localhost:5000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2026-04-27T..."
}
```

### Check Frontend
Open browser: http://localhost:3000

You should see the ResuMX login page.

---

## 🎯 Test the TPO Dashboard

1. **Sign up as TPO**:
   - Email: `tpo@college.edu`
   - Password: `password123`
   - Full Name: `John Doe`
   - Organization: `college.edu`
   - Role: `TPO`

2. **Navigate to TPO Dashboard**:
   - Click "TPO Dashboard" from landing page

3. **Go to Live Session Tab**:
   - Click "🔴 Live Session" tab

4. **Create a Session**:
   - Click "🚀 Start Session"
   - You'll see a session code (e.g., `COLLEGE-2026-A1`)

5. **Test Student Join** (New Incognito Window):
   - Sign up as student with same org domain
   - Click "Join Session"
   - Enter the session code
   - Student should appear in TPO dashboard

6. **Test Live Updates**:
   - Run a resume analysis as the student
   - Watch the TPO dashboard update (polls every 10 seconds)

7. **End Session**:
   - Click "⏹ End Session" in TPO dashboard
   - View the session summary

---

## 🔍 Troubleshooting

### Backend Won't Start

**Error**: `ModuleNotFoundError: No module named 'flask'`
```bash
cd backend
pip install -r requirements.txt
```

**Error**: `Port 5000 already in use`
```bash
# Windows: Find and kill process
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:5000 | xargs kill -9
```

### Frontend Won't Start

**Error**: `Cannot find module`
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Error**: `Port 3000 already in use`
```bash
# Change port in vite.config.js or kill process
# Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:3000 | xargs kill -9
```

### Network Error in TPO Dashboard

**Symptom**: Dashboard shows "Network error" or "Service unavailable"

**Solution**: Make sure backend is running!
```bash
# Check if backend is running
curl http://localhost:5000/api/health

# If not, start it
cd backend
python run.py
```

### CORS Errors

**Symptom**: Browser console shows CORS errors

**Solution**: Backend CORS is configured for `http://localhost:3000`. If you're using a different port, update `backend/app/__init__.py`:

```python
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://localhost:YOUR_PORT"],
        ...
    }
})
```

---

## 📋 Environment Variables

### Backend (.env)

Required variables are already set in `backend/.env`:
- ✅ `GROQ_API_KEY_1` through `GROQ_API_KEY_25` (25 keys configured)
- ✅ `JWT_SECRET` (⚠️ change for production!)
- ✅ `DATABASE_URL` (SQLite for dev)
- ✅ `FLASK_ENV=production`
- ✅ `PORT=5000`

### Frontend (.env)

Already configured in `frontend/.env`:
- ✅ `VITE_API_URL=/api` (proxied to backend)

---

## 🎓 User Roles

### TPO (Training & Placement Officer)
- Create live sessions
- View live dashboard
- End sessions
- View session summaries
- Generate batch reports
- Export student data

### Student
- Join sessions by code
- Run resume analysis
- View personal results
- Track progress

### Admin
- All TPO permissions
- Cross-organization access

---

## 📊 API Endpoints

### Health Check
```bash
GET http://localhost:5000/api/health
```

### Authentication
```bash
POST http://localhost:5000/api/auth/signup
POST http://localhost:5000/api/auth/login
POST http://localhost:5000/api/auth/refresh
```

### TPO Sessions
```bash
POST http://localhost:5000/api/tpo/sessions
POST http://localhost:5000/api/tpo/sessions/{id}/end
GET  http://localhost:5000/api/tpo/sessions/{id}/dashboard
GET  http://localhost:5000/api/tpo/sessions/{id}/summary
GET  http://localhost:5000/api/tpo/sessions
```

### Student Sessions
```bash
POST http://localhost:5000/api/sessions/join
```

---

## 🚀 Production Deployment

See [DEPLOYMENT_READINESS.md](DEPLOYMENT_READINESS.md) for full deployment guide.

**Quick checklist**:
1. Change `JWT_SECRET` in `backend/.env`
2. Use PostgreSQL instead of SQLite
3. Enable HTTPS
4. Set `FLASK_ENV=production`
5. Use Gunicorn for backend
6. Build frontend: `npm run build`
7. Serve frontend with nginx/Apache

---

## 📞 Need Help?

1. Check [DEPLOYMENT_READINESS.md](DEPLOYMENT_READINESS.md)
2. Check [ARCHITECTURE.md](ARCHITECTURE.md)
3. Check backend logs in terminal
4. Check browser console (F12)
5. Check network tab in browser DevTools

---

## ✅ Success Checklist

- [ ] Backend running on http://localhost:5000
- [ ] Frontend running on http://localhost:3000
- [ ] Can access login page
- [ ] Can sign up as TPO
- [ ] Can access TPO Dashboard
- [ ] Can see "Live Session" tab
- [ ] Can create a session
- [ ] Session code is displayed
- [ ] Can sign up as student (same org)
- [ ] Can join session with code
- [ ] Student appears in TPO dashboard
- [ ] Dashboard polls every 10 seconds
- [ ] Can end session
- [ ] Can view session summary

**If all checked**: 🎉 You're ready to go!
