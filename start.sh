#!/usr/bin/env bash
echo "Starting ScamShield AI - Scam Detection System..."

# Start backend
echo "Starting FastAPI Backend on http://127.0.0.1:8000 ..."
(cd backend && python run.py) &
BACKEND_PID=$!

# Start frontend
echo "Starting React Vite Frontend on http://localhost:5173 ..."
(cd frontend && npm run dev) &
FRONTEND_PID=$!

echo "ScamShield AI is running!"
echo "Frontend: http://localhost:5173"
echo "API Docs: http://127.0.0.1:8000/docs"

trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait
