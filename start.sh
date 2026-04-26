#!/bin/bash

# ResumeX - Quick Start Script for Linux/Mac

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║              ResumeX - AI Career Coach                    ║"
echo "║                   Quick Start Script                       ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Check if API key is set
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "⚠️  ANTHROPIC_API_KEY environment variable not set!"
    echo ""
    echo "Please set it before running:"
    echo "  export ANTHROPIC_API_KEY='your_api_key_here'"
    echo ""
    echo "Get your free API key at: https://console.anthropic.com"
    exit 1
fi

echo "✓ API Key found"
echo ""

# Setup Backend
echo "[1/4] Setting up Backend..."
cd backend

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing backend dependencies..."
pip install -r requirements.txt > /dev/null 2>&1

cd ..

# Setup Frontend
echo "[2/4] Setting up Frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install > /dev/null 2>&1
fi

cd ..

echo ""
echo "[3/4] Starting Backend Server..."
cd backend
source venv/bin/activate
python wsgi.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

echo ""
echo "[4/4] Starting Frontend Server..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                  ✅ Setup Complete!                        ║"
echo "╠════════════════════════════════════════════════════════════╣"
echo "║                                                            ║"
echo "║  Frontend:  http://localhost:3000                         ║"
echo "║  Backend:   http://localhost:5000                         ║"
echo "║                                                            ║"
echo "║  Servers are running in the background.                   ║"
echo "║  Open http://localhost:3000 in your browser!              ║"
echo "║                                                            ║"
echo "║  To stop servers, press Ctrl+C                            ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Keep script running
wait
