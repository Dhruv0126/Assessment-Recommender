# SHL Assessment Recommendation Assistant

A production-ready conversational AI assistant for SHL assessment recommendations using FastAPI (backend) + Streamlit (frontend) + RAG + Groq.

## Key Features

- **Dual-layer architecture**: FastAPI backend API + Streamlit web UI
- **Stateless conversation API** (`POST /chat`) with full message history tracking
- **SHL-only domain guardrails** with out-of-scope refusal
- **Smart clarification-first behavior** when role/seniority/focus information is missing
- **Vector-based retrieval** over SHL catalog embeddings (ChromaDB + Hugging Face)
- **Rich response schema** with recommendation details (duration, skills, test type, etc.)
- **Production-ready deployment** on Render with health checks
- **Ingestion pipeline** for catalog updates and data refresh

## Project Structure

```
SHL_RECOMMENDATION_APP/
├── app/                              # FastAPI backend service
│   ├── main.py                       # FastAPI app definition & endpoints
│   ├── models/
│   │   └── schemas.py                # Pydantic request/response models
│   ├── prompts/
│   │   └── system_prompt.py          # LLM system prompt
│   ├── services/
│   │   ├── agent.py                  # SHL agent orchestration logic
│   │   ├── catalog_store.py          # ChromaDB vector store interface
│   │   └── retriever.py              # RAG retrieval pipeline
│   └── utils/
│       └── text.py                   # Text utilities
├── data/
│   ├── shl_catalog.json              # SHL assessment catalog
│   └── chroma_db/                    # Vector database (ChromaDB)
├── scripts/
│   ├── ingest.py                     # Build/update vector database
│   └── scraper.py                    # Fetch SHL catalog data
├── streamlit_app.py                  # Streamlit web UI
├── requirements.txt                  # Python dependencies
├── .env.example                      # Environment variables template
└── README.md
```

## Quick Start

### 1. Environment Setup

```bash
# Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
copy .env.example .env
```

### 2. Configure Environment Variables

Edit `.env` and add:
- **`GROQ_API_KEY`**: Your Groq API key (get from https://console.groq.com)
- **`HF_TOKEN`**: Hugging Face token (get from https://huggingface.co/settings/tokens)
- **`HF_EMBED_BACKEND`**: 
  - `api` — use Hugging Face Inference API (requires internet, best for testing)
  - `local` — use sentence-transformers locally (recommended for production)
- **`API_BASE_URL`**: (optional) Deployed API URL for Streamlit to connect to

**Security Note**: Keep `.env` out of version control. `.env.example` is a template only—never commit real keys.

### 3. Build Vector Database

```bash
python scripts/ingest.py
```

This ingests the SHL catalog from `data/shl_catalog.json` into ChromaDB with embeddings.

### 4. Run Locally (Two Options)

**Option A: Run both services locally**

Terminal 1 (API):
```bash
uvicorn app.main:app --reload --port 8000
```

Terminal 2 (UI):
```bash
streamlit run streamlit_app.py
```

Then open http://localhost:8501 in your browser.

**Option B: Use deployed API + local UI**

Set `API_BASE_URL` in `.env` to your deployed backend URL, then run only Streamlit.

## API Endpoints

### `GET /`
Returns API metadata and documentation links.

```bash
curl http://localhost:8000/
```

### `GET /health`
Health check endpoint.

```bash
curl http://localhost:8000/health
```

Response:
```json
{ "status": "ok" }
```

### `POST /chat`
Main conversation endpoint. Returns AI reply and assessment recommendations.

**Request:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "I need an assessment for a backend Java developer"},
      {"role": "assistant", "content": "What seniority level and assessment focus?"},
      {"role": "user", "content": "Mid-level, focus on coding and communication"}
    ]
  }'
```

**Response:**
```json
{
  "reply": "Based on your requirements, I recommend the following SHL assessments...",
  "recommendations": [
    {
      "name": "SHL CAPP (Coding Assessment)",
      "url": "https://www.shl.com/...",
      "test_type": "C",
      "description": "Evaluates coding ability in Java",
      "duration": "45 minutes",
      "category": "Technical",
      "skills_measured": ["Java", "Problem Solving", "Algorithm Design"]
    }
  ],
  "end_of_conversation": false
}
```

## Agent Behavior

The assistant demonstrates intelligent multi-turn conversation handling:

- **Clarification**: Asks for missing context (role, seniority, focus areas)
- **Recommendation**: Suggests relevant SHL assessments with full details
- **Refinement**: Adjusts suggestions based on conversation history
- **Comparison**: Provides side-by-side assessment comparisons when requested
- **Domain Guardrails**: Politely declines non-SHL topics
- **Stateless Design**: All context comes from message history—no server-side session storage

## Technology Stack

- **Backend**: FastAPI + Uvicorn
- **Frontend**: Streamlit
- **LLM**: Groq (API inference)
- **Vector DB**: ChromaDB + Hugging Face embeddings
- **RAG Framework**: LangChain
- **Data Processing**: Beautiful Soup, Pydantic, NumPy

## Deployment

### Production Setup (Render)

1. Push code to GitHub (`.env` excluded)
2. Create Render Web Service pointing to your GitHub repo
3. Set environment variables in Render dashboard (GROQ_API_KEY, HF_TOKEN, etc.)
4. Deploy backend on Render (https://your-app.onrender.com)
5. Update Streamlit with `API_BASE_URL=https://your-app.onrender.com`
6. Optionally deploy Streamlit frontend on Streamlit Cloud

### Local Development

```bash
# Watch for code changes and auto-reload
uvicorn app.main:app --reload

# Or with a specific host/port
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Troubleshooting

**Embeddings API errors**: Switch from `HF_EMBED_BACKEND=api` to `HF_EMBED_BACKEND=local` in `.env`

**Vector DB missing**: Run `python scripts/ingest.py` to build ChromaDB

**API timeout**: Increase `REQUEST_TIMEOUT_SECONDS` in `streamlit_app.py`

## Contributing

To extend the assistant:

1. Update `data/shl_catalog.json` with new assessments
2. Re-run `python scripts/ingest.py`
3. Modify `app/prompts/system_prompt.py` for different behavior
4. Add new services in `app/services/` for custom logic

## License

Internal project. See project documentation for guidelines.
