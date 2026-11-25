#!/bin/bash
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
echo "==> CodeMentor — arranque local"

if [ ! -d "$ROOT/backend/venv" ]; then
  echo "Creando entorno virtual del backend..."
  python3 -m venv "$ROOT/backend/venv"
  source "$ROOT/backend/venv/bin/activate"
  pip install -r "$ROOT/backend/requirements.txt"
else
  source "$ROOT/backend/venv/bin/activate"
fi

echo "Iniciando backend en http://localhost:8000 ..."
cd "$ROOT/backend"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

cd "$ROOT/frontend"
if [ ! -d node_modules ]; then
  echo "Instalando dependencias del frontend..."
  npm install
fi

echo "Iniciando frontend en http://localhost:5173 ..."
npm run dev &
FRONTEND_PID=$!

echo ""
echo "CodeMentor listo."
echo "  Frontend: http://localhost:5173"
echo "  Backend:  http://localhost:8000"
echo "  API docs: http://localhost:8000/docs"
echo ""
echo "Presiona Ctrl+C para detener ambos servicios."
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT
wait
