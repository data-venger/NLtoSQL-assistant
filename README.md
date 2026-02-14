# ⚡ Warehouse SQL Assistant

AI-powered SQL assistant for banking data analysis. Ask questions in natural language — the AI generates SQL, executes it, and explains the results.

Built with a **RAG (Retrieval-Augmented Generation)** architecture: your question is embedded, matched against database schema vectors, and used to generate context-aware SQL queries.

---

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │     Backend      │    │     Ollama      │
│   (React+Vite)  │◄──►│    (Flask)       │◄──►│   (Local LLM)   │
│   Port: 5173    │    │   Port: 5001     │    │  Port: 11434    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                    ┌───────────┼───────────┐
                    │                       │
              ┌─────▼─────┐          ┌──────▼──┐
              │PostgreSQL  │          │ Qdrant  │
              │Port: 5432  │          │Port:6333│
              └────────────┘          └─────────┘
```

| Component | Role |
|-----------|------|
| **Frontend** | React + Vite UI with chat interface, SQL editor, schema explorer |
| **Backend** | Flask API — orchestrates the RAG pipeline |
| **PostgreSQL** | Banking database with 8 tables of sample data |
| **Qdrant** | Vector database storing schema embeddings for RAG search |
| **Ollama** | Local LLM (llama3.2) for SQL generation and response formatting |

---

## Features

| Feature | Description |
|---------|-------------|
| 💬 **Natural Language Chat** | Ask questions in plain English, get SQL + results |
| ⌨️ **Direct SQL Mode** | Write and execute SQL queries directly |
| 📊 **Schema Explorer** | Browse all tables and columns in the sidebar |
| 🕐 **Query History** | Re-run past queries with one click |
| 🔄 **Column Sorting** | Click column headers to sort results |
| 📄 **Pagination** | Navigate large result sets (15 rows/page) |
| 📥 **CSV Export** | Download any result as a CSV file |
| 🌙 **Dark/Light Mode** | Toggle theme, respects OS preference |
| 🔒 **Read-Only Safety** | Only SELECT queries allowed, with timeout protection |

---

## Prerequisites

Make sure you have the following installed before starting:

| Tool | Version | Check Command | Install |
|------|---------|---------------|---------|
| **Docker** | 20+ | `docker --version` | [docker.com](https://docs.docker.com/get-docker/) |
| **Docker Compose** | v2+ | `docker compose version` | Included with Docker Desktop |
| **Python** | 3.10+ | `python3 --version` | [python.org](https://www.python.org/downloads/) |
| **Node.js** | 18+ | `node --version` | [nodejs.org](https://nodejs.org/) |
| **npm** | 9+ | `npm --version` | Included with Node.js |

---

## Setup (First Time)

### Step 1: Clone / Navigate to the Project

```bash
cd /path/to/warehouse_sql_assistant
```

### Step 2: Start Database Services (Docker)

```bash
docker-compose up -d postgres qdrant
```

This starts:
- **PostgreSQL** on port `5432` — auto-creates the banking database with 8 tables and sample data
- **Qdrant** on port `6333` — vector database for schema embeddings

Verify they're running:
```bash
docker ps
```
You should see `wsa-postgres` (healthy) and `wsa-qdrant` (running).

### Step 3: Set Up the Backend

```bash
cd backend

# Create a Python virtual environment (first time only)
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

> ⚠️ **IMPORTANT**: You MUST run `source venv/bin/activate` every time you open a new terminal before running any Python commands. If you see `pip: command not found` or `ModuleNotFoundError`, you forgot to activate the venv.

### Step 4: Start the Backend Server

```bash
# Make sure venv is activated (you should see (venv) in your prompt)
source venv/bin/activate

# Start Flask server
python app.py
```

The backend runs on **http://localhost:5001**.

Verify it's working:
```bash
# In a separate terminal
curl http://localhost:5001/api/health
# Should return: {"status": "ok"}
```

### Step 5: Install & Start Ollama (AI/LLM)

**Install Ollama** (first time only):
```bash
# macOS — download from https://ollama.com/download
# Or via the install script:
curl -fsSL https://ollama.com/install.sh | sh
```

**Start the Ollama server:**
```bash
ollama serve
```

> On macOS, if `ollama` is not in your PATH, use the full path:
> ```bash
> /Applications/Ollama.app/Contents/Resources/ollama serve
> ```

**Pull the LLM model** (first time only — ~2GB download):
```bash
# In a separate terminal
ollama pull llama3.2
```

Verify Ollama is running:
```bash
curl http://localhost:11434/api/tags
# Should return a JSON with the llama3.2 model listed
```

### Step 6: Seed Schema Embeddings (First Time Only)

This populates Qdrant with vector embeddings of the database schema so the AI knows which tables/columns exist:

```bash
cd backend
source venv/bin/activate
python ../scripts/seed_schemas.py
```

Expected output:
```
🔄 Seeding schema embeddings into Qdrant...
✅ Embedded 8 table schemas successfully!
📊 Verified 8 schemas in Qdrant
```

### Step 7: Install & Start the Frontend

```bash
cd frontend

# Install Node dependencies (first time only)
npm install

# Start the dev server
npm run dev
```

The frontend runs on **http://localhost:5173**.

### Step 8: Open the App! 🎉

Open your browser and go to: **http://localhost:5173**

Try typing: *"How many customers do we have?"*

---

## Running After First Setup

Once everything is set up, here's the quick-start for subsequent runs:

```bash
# Terminal 1 — Docker (if not already running)
cd /path/to/warehouse_sql_assistant
docker-compose up -d postgres qdrant

# Terminal 2 — Backend
cd /path/to/warehouse_sql_assistant/backend
source venv/bin/activate
python app.py

# Terminal 3 — Ollama
ollama serve
# Or: /Applications/Ollama.app/Contents/Resources/ollama serve

# Terminal 4 — Frontend
cd /path/to/warehouse_sql_assistant/frontend
npm run dev
```

Then open **http://localhost:5173**.

---

## Environment Variables

The `.env` file in the project root controls all configuration. Default values work out of the box for local development:

```env
# Database
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=banking_db
DATABASE_USER=postgres
DATABASE_PASSWORD=postgres

# AI Services
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
QDRANT_URL=http://localhost:6333
LLM_PROVIDER=ollama          # Options: ollama, gemini

# If using Gemini instead of Ollama:
# GEMINI_API_KEY=your-api-key-here
# LLM_PROVIDER=gemini

# Security
SECRET_KEY=dev-secret-key-change-in-production
QUERY_TIMEOUT=30
MAX_QUERY_ROWS=1000

# Flask
FLASK_DEBUG=true
```

---

## Database Schema

The banking database contains 8 interconnected tables:

| Table | Rows | Description |
|-------|------|-------------|
| `branches` | 5 | Bank branch locations |
| `customers` | 20 | Customer demographics & financials |
| `accounts` | 30 | Checking, savings, money market accounts |
| `transactions` | 50+ | Deposits, withdrawals, transfers |
| `credit_cards` | 8 | Card details, limits, balances |
| `credit_card_transactions` | 14 | Card purchases and payments |
| `loans` | 10 | Mortgage, personal, auto, business loans |
| `loan_payments` | 20+ | Payment records with principal/interest |

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/health` | Health check |
| `POST` | `/api/chat` | Send a natural language query (RAG pipeline) |
| `GET` | `/api/database/test` | Test database connection |
| `GET` | `/api/database/tables` | List all tables with row counts |
| `GET` | `/api/database/tables/<name>` | Get column details for a table |
| `POST` | `/api/database/execute` | Execute a SQL query directly |
| `POST` | `/api/embeddings/embed` | Embed a schema into Qdrant |
| `POST` | `/api/embeddings/search` | Search similar schemas |
| `GET` | `/api/embeddings/schemas` | List all stored schemas |

---

## Troubleshooting

### `pip: command not found` or `ModuleNotFoundError`
You forgot to activate the virtual environment:
```bash
cd backend
source venv/bin/activate
```

### `Port 5001 is in use`
The backend is already running. Either:
- Use the existing instance, or
- Kill it: `lsof -ti:5001 | xargs kill -9`

### `Port 5000 is in use` (macOS)
macOS AirPlay Receiver uses port 5000. Our backend uses **port 5001** to avoid this conflict.

### `Address already in use` for Ollama (port 11434)
Ollama is already running. Check with:
```bash
curl http://localhost:11434/api/tags
```
If it responds, Ollama is fine — no need to start it again.

### Docker containers not starting
```bash
# Check container status
docker ps -a

# View logs
docker logs wsa-postgres
docker logs wsa-qdrant

# Restart from scratch
docker-compose down -v
docker-compose up -d postgres qdrant
```
> ⚠️ `docker-compose down -v` deletes all data. You'll need to re-seed schemas after.

### Chat returns errors but Direct SQL works
Make sure:
1. Ollama is running (`curl http://localhost:11434/api/tags`)
2. The llama3.2 model is pulled (`ollama list` should show it)
3. Schema embeddings are seeded (run `python ../scripts/seed_schemas.py`)

### Frontend shows "Disconnected"
The backend isn't reachable. Make sure:
1. Backend is running on port 5001
2. Vite proxy is configured for port 5001 (check `frontend/vite.config.js`)

---

## Project Structure

```
warehouse_sql_assistant/
├── .env                          # Environment variables
├── .env.example                  # Environment template
├── .gitignore
├── docker-compose.yml            # PostgreSQL + Qdrant services
├── README.md
│
├── backend/
│   ├── Dockerfile
│   ├── app.py                    # Flask entry point
│   ├── config.py                 # Configuration loader
│   ├── requirements.txt          # Python dependencies
│   ├── routes/
│   │   ├── chat.py               # RAG pipeline API
│   │   ├── database.py           # Database query API
│   │   └── embeddings.py         # Schema embedding API
│   └── services/
│       ├── database_service.py   # Safe SQL execution
│       ├── embedding_service.py  # Qdrant + SentenceTransformers
│       └── llm_client.py         # Ollama/Gemini LLM client
│
├── frontend/
│   ├── Dockerfile
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   └── src/
│       ├── App.jsx               # Main application
│       ├── api.js                # API client
│       ├── index.css             # Design system
│       ├── main.jsx              # React entry
│       └── components/
│           ├── QueryHistory.jsx  # Query history sidebar
│           ├── ResultTable.jsx   # Sortable, paginated results
│           ├── SchemaExplorer.jsx # Database schema browser
│           └── SqlBlock.jsx      # SQL display with highlighting
│
├── data/
│   ├── 01_banking_schema.sql     # Database DDL
│   └── 02_banking_data.sql       # Sample data
│
└── scripts/
    └── seed_schemas.py           # Seed Qdrant with schema embeddings
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 18 + Vite 6 |
| Backend | Flask (Python 3.11) |
| LLM | Ollama (llama3.2) / Gemini API |
| Vector DB | Qdrant |
| Database | PostgreSQL 15 |
| Embeddings | SentenceTransformers (all-MiniLM-L6-v2) |
