# SHL Assessment Recommendation Assistant

<div style="display:flex;gap:16px;align-items:center;flex-wrap:wrap">
  <img src="Images/Screenshot%202026-06-07%20184359.png" alt="SHL Recommendation Assistant - Screenshot 1" style="width:48%;max-width:560px;border-radius:8px;box-shadow:0 6px 18px rgba(0,0,0,0.12)" />
  <img src="Images/Screenshot%202026-06-07%20184030.png" alt="SHL Recommendation Assistant - Screenshot 2" style="width:48%;max-width:560px;border-radius:8px;box-shadow:0 6px 18px rgba(0,0,0,0.12)" />
</div>

A modern AI-powered recommendation assistant that helps HR and talent teams find the right SHL assessment using conversational inputs, semantic search, and smart prompt orchestration.

---

## 🌟 Live Demo

Visit the deployed app:

https://dhruv0126-assessment-recommender-dhruv0126.streamlit.app/

---

## 🚀 What this project does

This app turns natural conversation into SHL assessment recommendations by combining:

- **FastAPI backend** for a stateless chat API
- **Streamlit frontend** for an intuitive recommendation UI
- **Retrieval-Augmented Generation (RAG)** over SHL assessment content
- **ChromaDB vector search** for fast similarity-based retrieval
- **Hugging Face embeddings** + **Groq LLM** inference
- **Domain guardrails** for SHL-only responses and safety

---

## 📌 Key Features

- **Conversational recommendation flow** with history-aware responses
- **Clarification-first behavior** for missing role, seniority, or focus
- **Structured recommendation output** including duration, skills, test type, and category
- **Searchable SHL catalog** via vector embeddings and metadata
- **Production-ready deployment support** with health checks
- **Data refresh pipeline** for catalog updates and ingestion

---

## 🧩 Project Structure

```text
SHL_RECOMMENDATION_APP/
├── app/
│   ├── main.py
│   ├── models/
│   │   └── schemas.py
│   ├── prompts/
│   │   └── system_prompt.py
│   ├── services/
│   │   ├── agent.py
│   │   ├── catalog_store.py
│   │   └── retriever.py
│   └── utils/
│       └── text.py
├── data/
│   ├── shl_catalog.json
│   └── chroma_db/
├── scripts/
│   ├── ingest.py
│   └── scraper.py
├── streamlit_app.py
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🧠 How it works

1. **Ingest SHL data** from `data/shl_catalog.json`.
2. **Compute embeddings** for catalog entries using Hugging Face.
3. **Persist vectors** into ChromaDB (`data/chroma_db/`).
4. **Accept chat requests** via `POST /chat`.
5. **Retrieve relevant assessments** using similarity search.
6. **Compose prompts** for Groq-based reasoning.
7. **Return curated recommendations** with full details.

---

## 💻 Setup & Local Run

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Edit `.env` and set:

- `GROQ_API_KEY`
- `HF_TOKEN`
- `HF_EMBED_BACKEND` = `api` or `local`
- `API_BASE_URL` when using a deployed backend

Build the vector database:

```powershell
python scripts/ingest.py
```

Run the backend:

```powershell
uvicorn app.main:app --reload --port 8000
```

Run the Streamlit UI:

```powershell
streamlit run streamlit_app.py
```

Open the app at `http://localhost:8501`

---

## 🔧 API Endpoints

### `GET /`

Returns API metadata and docs links.

### `GET /health`

Health check response:

```json
{ "status": "ok" }
```

### `POST /chat`

Request example:

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

Response example:

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

---

## ✨ Agent Behavior

This solution is designed for intelligent recommendation workflows:

- **Clarification** on missing details such as seniority or focus area
- **Recommendation** of best-fit SHL assessments
- **Refinement** based on updated user context
- **Comparison** of comparable tests on request
- **Domain safety** that refuses out-of-scope requests
- **Stateless design** using only message history

---

## 📦 Technology Stack

- **Backend**: FastAPI + Uvicorn
- **Frontend**: Streamlit
- **Vector DB**: ChromaDB
- **Embeddings**: Hugging Face or local `sentence-transformers`
- **LLM**: Groq API
- **RAG**: LangChain
- **Data tools**: BeautifulSoup, Pydantic, NumPy

---

## 🛠️ Deployment

Deployed frontend link:

https://dhruv0126-assessment-recommender-dhruv0126.streamlit.app/

### Render / cloud deployment notes

- Push code to GitHub (exclude `.env`)
- Configure environment secrets in Render
- Deploy backend service
- Point Streamlit or frontend to `API_BASE_URL`

---

## 🧪 Troubleshooting

- If embeddings fail: switch `HF_EMBED_BACKEND=local`
- If the vector DB is missing: run `python scripts/ingest.py`
- If API calls timeout: increase `REQUEST_TIMEOUT_SECONDS` in `streamlit_app.py`

---

## 📈 How to extend

- Add new assessments to `data/shl_catalog.json`
- Re-run `python scripts/ingest.py`
- Adjust `app/prompts/system_prompt.py` for behavior changes
- Add new retrieval or recommendation logic in `app/services/`

---

## 📝 Notes

This repo is built for internal use and can be extended into a stronger talent assessment recommendation engine with better evaluation metrics, richer UI flows, and stronger production monitoring.
