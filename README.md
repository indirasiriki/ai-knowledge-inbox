# AI Knowledge Inbox

A minimal, production-style web app that lets you save notes or web links and ask questions powered by a RAG (Retrieval-Augmented Generation) pipeline with cited sources.

---

## Quick Start

### 1. Prerequisites
- **Node.js**: v20 or newer
- **Python**: v3.11 or newer

### 2. Install Dependencies
```powershell
# Install frontend packages
npm install

# Create virtual environment and install backend packages
python -m venv server\.venv
server\.venv\Scripts\python.exe -m pip install -r server\requirements.txt
```
*(On Windows PowerShell, use `npm.cmd` if your terminal restricts running scripts).*

### 3. Add OpenAI API Key
Copy the example environment file:
```powershell
copy server\.env.example server\.env
```
Open `server\.env` and set your key:
```env
OPENAI_API_KEY=sk-your-openai-api-key
```

### 4. Start the Application

#### Development Mode (FastAPI + Vite together)
```powershell
npm run dev
```
- Frontend: **http://localhost:5173**
- Backend API: **http://localhost:3001**

#### Production Mode (FastAPI serves built React app)
```powershell
npm run build
npm start
```
- Open **http://localhost:3001**

### 5. Run Tests
```powershell
npm test
```
Runs the full pytest test suite (27 tests covering chunking, vector math, HTML extraction, SSRF URL checks, database transactions, and HTTP status codes). No OpenAI credits are consumed during tests.

---

## Available Commands

| Command | Description |
| --- | --- |
| `npm run dev` | Runs FastAPI (port 3001) and Vite dev server (port 5173) together |
| `npm test` | Runs all 27 unit & integration tests with pytest |
| `npm run build` | Builds the React frontend bundle into `client/dist` |
| `npm start` | Runs FastAPI serving both the API and the built frontend on port 3001 |

---

## How It Works

### Ingestion Pipeline
1. **Input:** Save a text note or a web URL.
2. **Page Fetching:** URLs are fetched server-side with SSRF protection (private/loopback IPs rejected). HTML is cleaned to readable text.
3. **Chunking:** Text is split into ~900-character chunks with 150-character overlap, snapping to paragraph, sentence, and word boundaries.
4. **Embeddings:** Chunks are vectorized using OpenAI's `text-embedding-3-small`.
5. **Storage:** Item metadata and chunk vectors (stored as 32-bit float blobs) are saved in SQLite within an atomic transaction.

### RAG Query Pipeline
1. **Query Embedding:** User question is embedded with `text-embedding-3-small`.
2. **Vector Search:** Fast in-memory cosine similarity search retrieves top matching chunks (default: top 5 with score $\ge 0.22$).
3. **Answer Generation:** Retrieved chunks and question are sent to `gpt-4o-mini` with a prompt enforcing answers grounded strictly in the saved notes with citations (`[1]`, `[2]`).
4. **Sources Display:** UI shows the answer along with numbered source cards, matching snippets, and relevance scores.

---

## API Endpoints

Supports both the assessment standard endpoints and `/api/*` endpoints:

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/ingest` or `/api/items` | Ingest note (`{ "text": "..." }`) or URL (`{ "url": "..." }`) |
| `GET` | `/items` or `/api/items` | List all saved items (summaries, excerpts, chunk counts) |
| `DELETE` | `/items/:id` or `/api/items/:id` | Delete an item and its vector chunks |
| `POST` | `/query` or `/api/questions` | Ask a question (`{ "question": "..." }` or `{ "query": "..." }`) |
| `GET` | `/api/health` | Health check & OpenAI key status |

### Example Ingest Requests
```json
// Note
POST /ingest
{ "sourceType": "note", "text": "Deploy window is Thursday 16:00 UTC." }

// Link
POST /ingest
{ "sourceType": "url", "url": "https://example.com/article" }
```

### Example Query Request
```json
POST /query
{ "question": "When is the deploy window?" }
```

---

## Design Decisions & Tradeoffs

### System Architecture Decisions
- **Separation of Concerns:** Clean boundary between storage/retrieval (`server/`) and the user interface (`client/`).
- **Zero-Bloat Infrastructure:** Uses an embedded SQLite file with WAL mode instead of managing external vector database services or Docker containers.
- **Dual-Mode RAG Support:** Supports live OpenAI models (`text-embedding-3-small` and `gpt-4o-mini`) when `OPENAI_API_KEY` is provided, while offering an offline local fallback so developers can run, test, and evaluate the system without external API dependencies.
- **Security & Guardrails:** Server-side URL scraper rejects private, loopback, and local network IPs (SSRF protection), enforces request timeouts, size caps, and hops limits.

### 1. Chunking Strategy Rationale
- **Approach:** 900-character target window with 150-character overlap and boundary snapping in the last 280 characters.
- **Why:** Preserves semantic meaning by breaking at natural points (paragraphs, sentences, words) rather than abruptly cutting words or sentences in half.
- **Size Tradeoff:** ~900 characters (~200 tokens) provides enough context for the LLM while staying focused enough for accurate similarity retrieval.

### 2. Vector Store Choice
- **Approach:** SQLite with raw float32 BLOB storage and in-memory cosine similarity ranking.
- **Why:** Zero infrastructure bloat (no extra daemon, Docker, or external vector service). ACID compliance ensures items and chunks persist together. Cascading deletes remove chunks automatically when an item is deleted. Very fast (<10ms) for personal inbox scale.

### 3. What Breaks at Scale
- **In-Memory Vector Scan:** Full table scan $O(N)$ dot products will consume excessive memory and CPU beyond ~50k–100k chunks.
- **SQLite Single Writer:** SQLite allows only one writer at a time, creating a bottleneck under concurrent multi-user ingestion.
- **Synchronous Ingestion:** Fetching external URLs and generating embeddings synchronously in the request loop increases latency and risk of timeouts.

### 4. Production Changes
- **Vector Index:** Switch to an Approximate Nearest Neighbor (ANN) index (e.g. HNSW via `pgvector`, `sqlite-vss`, or Qdrant).
- **Background Jobs:** Move URL scraping and embedding generation to an asynchronous queue (Celery, BullMQ, or Redis Streams).
- **Multi-Tenancy & Auth:** Migrate to PostgreSQL for connection pooling, row-level security (RLS), and user authentication.
- **Streaming & Cache:** Stream LLM responses via Server-Sent Events (SSE) and cache repeat query embeddings in Redis.

---

## Project Structure

```
├── client/                 # React 18 + Vite + Tailwind CSS frontend
│   ├── src/
│   │   ├── api/client.js   # Central API fetch client
│   │   ├── components/     # UI components (Composer, SavedList, AskPanel, SourceList)
│   │   ├── hooks/          # React hooks (useItems, useQuestion, useServerStatus)
│   │   └── App.jsx         # Main application layout
├── server/                 # FastAPI backend
│   ├── app/
│   │   ├── db/             # SQLite connection, schema, and repositories
│   │   ├── routes/         # API route handlers (items, questions)
│   │   ├── services/       # RAG pipeline: chunking, embedding, retrieval, LLM
│   │   ├── factory.py      # App factory, CORS, static serving, error handlers
│   │   └── main.py         # Entry point for Uvicorn
│   ├── tests/              # Pytest test suite (27 unit & integration tests)
│   ├── requirements.txt    # Python dependencies
│   └── .env.example        # Environment variable template
├── scripts/                # Node runner scripts for dev and start
├── package.json            # Workspace root scripts
└── README.md               # Documentation
```
