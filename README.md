# RepoMind AI

Ask questions about any GitHub repository and get answers with the exact files and line ranges they come from. Everything runs locally: local embeddings, a local vector database, and a local LLM.

<!-- Add a screenshot or GIF here: docs/screenshot.png -->
<!-- ![RepoMind AI](docs/screenshot.png) -->

RepoMind is **not** a code-generation tool. It helps you *understand* unfamiliar code:

- Where is authentication implemented?
- How does login work?
- Where are the API routes defined?
- How is error handling done?
- What does this repository do?

## How it works

```text
Index   GitHub URL → validate → shallow clone → parse files
        → chunk (100 lines, 20 overlap) → embed (bge-small-en-v1.5, 384-d)
        → store in Qdrant with repository_id

Ask     question → embed → Qdrant search filtered by repository_id (top 20)
        → drop tests / CI / changelog noise → keep best 5
        → build prompt → Ollama (qwen2.5-coder:3b)
        → answer + sources (file, line range, score)
```

### Design decisions

- **Per-repository isolation.** Every vector stores a `repository_id`, and every search filters on it. One Qdrant collection serves many repositories without results leaking between them.
- **Over-fetch, then filter.** Qdrant returns 20 candidates, noisy files (tests, CI configs, changelogs) are removed, and the best 5 remain. Taking only the top 5 first often left nothing useful after filtering.
- **Line-based chunks with overlap.** Simple, and it gives exact line numbers for source citations.
- **PostgreSQL as source of truth.** It stores repository metadata and status (`PENDING`, `READY`, `FAILED`). Qdrant stores only vectors.
- **Idempotent indexing.** Submitting an already-indexed URL returns the existing record. URL variants (trailing slash, `.git`) map to one repository, and failed repositories are retried cleanly.
- **Safe deletion.** Deleting a repository removes its vectors and local clone first and the database row last, so a failed cleanup can be retried.
- **Custom orchestration.** The pipeline is plain services (parser, chunker, embedder, indexer, retriever, prompt builder, LLM, chat) with no LangChain or similar framework, so each RAG stage is visible in the code.

## Tech stack

| Layer | Tools |
|---|---|
| Backend | FastAPI, SQLAlchemy, Alembic, GitPython |
| Database | PostgreSQL |
| Vector store | Qdrant (cosine distance) |
| Embeddings | `BAAI/bge-small-en-v1.5` via Sentence Transformers |
| LLM | Ollama, `qwen2.5-coder:3b` by default |
| Frontend | React, Vite, Tailwind CSS |

## Project structure

```text
backend/
├── app/
│   ├── main.py
│   ├── core/            # settings
│   ├── database/        # session and dependencies
│   ├── models/          # SQLAlchemy models, enums
│   ├── schemas/         # Pydantic schemas
│   ├── routes/          # repository.py, chat.py
│   └── services/
│       ├── repository_service.py   # clone + index lifecycle, list, delete
│       ├── parser_service.py       # find source files
│       ├── chunking_service.py     # split files into chunks
│       ├── embedding_service.py    # local embeddings
│       ├── indexing_service.py     # parse → chunk → embed → store
│       ├── qdrant_service.py       # vector store access
│       ├── retrieval_service.py    # filtered search + noise removal
│       ├── prompt_service.py       # RAG prompt
│       ├── llm_service.py          # Ollama client
│       └── chat_service.py         # retrieval + prompt + LLM
├── alembic/
└── repositories/        # cloned repositories (git-ignored)

frontend/
└── src/
    ├── App.jsx
    ├── components/      # Sidebar, AddRepository, ChatView, icons
    └── services/api.js
```

## Getting started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker (for PostgreSQL and Qdrant)
- [Ollama](https://ollama.com)

### 1. Start PostgreSQL and Qdrant

```bash
docker run -d --name repomind-postgres \
  -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=repomind \
  -p 5432:5432 postgres:16

docker run -d --name repomind-qdrant \
  -p 6333:6333 qdrant/qdrant
```

### 2. Start Ollama and pull the model

```bash
ollama pull qwen2.5-coder:3b
ollama serve   # skip if Ollama is already running
```

### 3. Run the backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env     # then edit values to match your setup
alembic upgrade head
uvicorn app.main:app --reload --port 8001
```

API docs: http://127.0.0.1:8001/docs

### 4. Run the frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173, paste a public GitHub URL (for example `https://github.com/psf/requests`), wait for indexing to finish, and start asking questions.

> The frontend calls the backend at `http://127.0.0.1:8001/api/v1` (see `frontend/src/services/api.js`). The backend must allow `http://localhost:5173` in its CORS settings.

## API

All routes are under `/api/v1`.

| Method | Path | Description |
|---|---|---|
| `GET` | `/repositories` | List indexed repositories |
| `POST` | `/repositories` | Index a repository: `{"github_url": "https://github.com/owner/repo"}`. Returns the existing record if already indexed |
| `DELETE` | `/repositories/{id}` | Delete the repository's vectors, local clone, and database row |
| `POST` | `/chat/` | Ask a question: `{"repository_id": 1, "question": "..."}` |

Example:

```bash
curl -X POST http://127.0.0.1:8001/api/v1/chat/ \
  -H "Content-Type: application/json" \
  -d '{"repository_id": 1, "question": "Where is authentication implemented?"}'
```

Response:

```json
{
  "answer": "Authentication is implemented in ...",
  "sources": [
    { "file_path": "src/requests/auth.py", "start_line": 1, "end_line": 100, "score": 0.70 }
  ]
}
```

## Limitations

- **Indexing is synchronous.** `POST /repositories` blocks until cloning and embedding finish. Large repositories can take minutes.
- **No conversation memory.** Each question is answered independently; earlier messages are not sent to the model.
- **Broad questions are weaker.** Questions like "what does this repo do?" don't yet prioritize the README.
- **Small local model.** A 3B model is less reliable than hosted models on complex reasoning. The LLM is configurable via `LLM_MODEL`.
- **Semantic search only.** Exact identifier lookups can miss; there is no keyword or hybrid search yet.
- **Public repositories only.** Private repositories are not supported.

## Roadmap

- Background indexing with a job queue and progress reporting
- Conversation history in prompts for follow-up questions
- README prioritization and reranking for broad questions
- Hybrid search (keyword + vector)
- Syntax-aware chunking (functions and classes) instead of fixed line windows
- Re-indexing on new commits

## License

Add a license of your choice (for example MIT) before sharing the repository publicly.