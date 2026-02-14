#!/bin/bash
set -e
echo ""
echo "Warehouse SQL Assistant — Setup"
echo ""

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "Checking prerequisites..."

command -v docker >/dev/null 2>&1 || { echo " Docker not installed. Get it at https://docs.docker.com/get-docker/"; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo " Python 3 not installed. Get it at https://python.org"; exit 1; }
command -v node >/dev/null 2>&1 || { echo " Node.js not installed. Get it at https://nodejs.org"; exit 1; }
echo " All prerequisites found"

if [ ! -f "$PROJECT_DIR/.env" ]; then
    cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
    echo " Created .env from .env.example"
fi

echo ""
echo "Starting PostgreSQL and Qdrant..."
cd "$PROJECT_DIR"
docker-compose up -d postgres qdrant 2>&1 | grep -v "WARN" || true

echo -n "Waiting for PostgreSQL..."
for i in {1..30}; do
    docker exec wsa-postgres pg_isready -U postgres &>/dev/null && break
    echo -n "."
    sleep 2
done
echo " ready"

echo ""
echo "Setting up backend..."
cd "$PROJECT_DIR/backend"

[ ! -d "venv" ] && python3 -m venv venv
./venv/bin/pip install -q -r requirements.txt 2>&1 | tail -1
echo " Backend ready OK"

echo ""
echo "Setting up frontend..."
cd "$PROJECT_DIR/frontend"
[ ! -d "node_modules" ] && npm install --silent
echo " Frontend ready OK"

echo ""
echo "Checking Ollama..."
OLLAMA_BIN=$(command -v ollama 2>/dev/null || echo "/Applications/Ollama.app/Contents/Resources/ollama")

if [ ! -f "$OLLAMA_BIN" ] && ! command -v ollama &>/dev/null; then
    echo "  Ollama not installed — install from https://ollama.com/download"
    echo "   Direct SQL mode will still work without it."
else
    
    if ! curl -s http://localhost:11434/api/tags &>/dev/null; then
        "$OLLAMA_BIN" serve &>/dev/null &
        sleep 3
    fi
    echo " Ollama running"

    if ! curl -s http://localhost:11434/api/tags 2>/dev/null | grep -q "llama3.2"; then
        echo "Pulling llama3.2 (~2GB)..."
        "$OLLAMA_BIN" pull llama3.2
    fi
    echo " llama3.2 model ready"
fi

echo ""
cd "$PROJECT_DIR"
SCHEMA_COUNT=$(curl -s http://localhost:6333/collections/schema_embeddings 2>/dev/null | python3 -c "import sys,json; print(json.load(sys.stdin).get('result',{}).get('points_count',0))" 2>/dev/null || echo "0")

if [ "$SCHEMA_COUNT" -lt 8 ]; then
    echo "Seeding schema embeddings..."
    "$PROJECT_DIR/backend/venv/bin/python" "$PROJECT_DIR/scripts/seed_schemas.py"
else
    echo " Schemas already seeded"
fi

# --- Done ---
echo ""
echo "==================================="
echo " Setup complete!"
echo "==================================="
echo ""
echo "Start the app:"
echo ""
echo "  Terminal 1:  cd backend && source venv/bin/activate && python app.py"
echo "  Terminal 2:  cd frontend && npm run dev"
echo ""
echo "  Then open:   http://localhost:5173"
echo ""

read -p "Start now? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    lsof -ti:5001 | xargs kill 2>/dev/null || true
    sleep 1

    cd "$PROJECT_DIR/backend"
    source venv/bin/activate
    python app.py &

    cd "$PROJECT_DIR/frontend"
    npm run dev &

    sleep 3
    echo ""
    echo " App is live at http://localhost:5173"
    echo "   Press Ctrl+C to stop"

    command -v open &>/dev/null && open http://localhost:5173

    trap "kill $(jobs -p) 2>/dev/null; echo 'Stopped.'; exit 0" SIGINT
    wait
fi
