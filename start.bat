@echo off
REM AI Resume Analyzer - Quick Start Script
REM This script sets up and runs the complete application

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║       AI Resume Analyzer - Full Stack Application         ║
echo ║                   Quick Start Script                       ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

REM Using Groq API - no ANTHROPIC_API_KEY needed
echo ✓ Groq API configured
echo.

REM Setup Backend
echo [1/4] Setting up Backend...
cd backend

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing backend dependencies...
pip install -r requirements.txt > nul 2>&1

cd ..

REM Setup Frontend
echo [2/4] Setting up Frontend...
cd frontend

if not exist "node_modules" (
    echo Installing frontend dependencies...
    npm install > nul 2>&1
)

cd ..

echo.
echo [3/4] Starting Backend Server...
echo Opening terminal for backend...
start cmd /k "cd backend && venv\Scripts\activate.bat && python wsgi.py"

REM Wait for backend to start
timeout /t 3 /nobreak

echo.
echo [4/4] Starting Frontend Server...
echo Opening terminal for frontend...
start cmd /k "cd frontend && npm run dev"

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                  ✅ Setup Complete!                        ║
echo ╠════════════════════════════════════════════════════════════╣
echo ║                                                            ║
echo ║  Frontend:  http://localhost:3000                         ║
echo ║  Backend:   http://localhost:5000                         ║
echo ║                                                            ║
echo ║  Both servers are starting in new terminals.              ║
echo ║  Please wait 10-15 seconds for both to fully load.        ║
echo ║                                                            ║
echo ║  Open http://localhost:3000 in your browser!              ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

pause
