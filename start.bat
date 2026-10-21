@echo off
echo ========================================================
echo Starting ScamShield AI - Scam Detection System
echo ========================================================

echo 1. Starting FastAPI Backend on http://127.0.0.1:8000 ...
start "ScamShield Backend" cmd /k "cd backend && python run.py"

echo 2. Starting React Vite Frontend on http://localhost:5173 ...
start "ScamShield Frontend" cmd /k "cd frontend && npm run dev"

echo ========================================================
echo System online!
echo Frontend: http://localhost:5173
echo Backend API Docs: http://127.0.0.1:8000/docs
echo ========================================================
pause
