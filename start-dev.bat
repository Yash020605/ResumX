@echo off
REM Quick start script for development (Windows)

echo 🚀 Starting ResuMX Development Servers...
echo.

REM Check if backend venv exists
if not exist "backend\venv" (
    echo 📦 Creating Python virtual environment...
    cd backend
    python -m venv venv
    cd ..
)

REM Start backend in new window
echo 🔧 Starting Backend Server (Flask)...
start "ResuMX Backend" cmd /k "cd backend && venv\Scripts\activate && pip install -q -r requirements.txt && python run.py"

echo ✅ Backend starting on http://localhost:5000
echo.

REM Wait for backend to be ready
echo ⏳ Waiting for backend to be ready...
timeout /t 5 /nobreak > nul

echo.

REM Start frontend in new window
echo 🎨 Starting Frontend Server (Vite)...
cd frontend

REM Check if node_modules exists
if not exist "node_modules" (
    echo 📦 Installing npm dependencies...
    call npm install
)

start "ResuMX Frontend" cmd /k "npm run dev"
cd ..

echo ✅ Frontend starting on http://localhost:3000
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 🎉 ResuMX is running!
echo.
echo 📍 Frontend: http://localhost:3000
echo 📍 Backend:  http://localhost:5000
echo 📍 API Docs: http://localhost:5000/api/health
echo.
echo Close the terminal windows to stop the servers
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
pause
