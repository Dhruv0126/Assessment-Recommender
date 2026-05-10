# SHL Assessment Recommendation Assistant

A production-style starter for a stateless conversational SHL assessment assistant using FastAPI + RAG + Groq.

## What this project includes

- Stateless conversation API (`POST /chat`) with full message history input.
- SHL-only domain guardrails (out-of-scope refusal).
- Clarification-first behavior when role/seniority/focus are missing.
- ChromaDB retrieval over SHL catalog embeddings.
- Recommendation and comparison-ready response schema.
- Ingestion pipeline and scraper template.

## Project structure

```text
project/
├── app/
│   ├── main.py
│   ├── models/schemas.py
│   ├── prompts/system_prompt.py
│   ├── services/
│   │   ├── agent.py
│   │   ├── catalog_store.py
│   │   └── retriever.py
│   └── utils/text.py
├── data/
│   ├── shl_catalog.json
│   └── chroma_db/
├── scripts/
│   ├── scraper.py
│   └── ingest.py
├── requirements.txt
└── README.md
```

## 1) Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Set your Groq and Hugging Face keys in `.env`.

- **`HF_EMBED_BACKEND=api`**: embeddings via Hugging Face Inference (requires token; routed by `huggingface_hub`).
- **`HF_EMBED_BACKEND=local`**: embeddings on your machine with `sentence-transformers` (faster for large catalogs; recommended if Inference returns errors for your model).

The committed **`.env.example`** is only a template (no secrets). Copy it to **`.env`**, fill in keys, and keep **`.env` out of git**—your real **`.env`** is what the app reads.

## 2) Build vector DB

```bash
python scripts/ingest.py
```

## 3) Run API

```bash
uvicorn app.main:app --reload
```

## 4) Endpoints

### `GET /health`

Response:

```json
{
  "status": "ok"
}
```

### `POST /chat`

Request:

```json
{
  "messages": [
    {"role": "user", "content": "Need assessment for backend Java developer"},
    {"role": "assistant", "content": "What seniority and assessment focus?"},
    {"role": "user", "content": "Mid-level, coding + communication"}
  ]
}
```

Response schema:

```json
{
  "reply": "string",
  "recommendations": [
    {
      "name": "string",
      "url": "https://...",
      "test_type": "K",
      "description": "string",
      "duration": "string",
      "category": "string",
      "skills_measured": ["string"]
    }
  ],
  "end_of_conversation": false
}
```

## Behavior covered

- Clarification when request is vague.
- Recommendation when enough context exists.
- Refinement via full conversation history.
- Comparison via retrieved catalog context.
- Refusal for non-SHL topics.

## Next improvements (for submission strength)

- Improve scraper selectors for complete SHL catalog fields.
- Add hybrid ranking (similarity + keyword + skill overlap scoring).
- Add unit tests for clarify/refuse/refine/compare behavior.
- Add evaluation scripts for Recall@10 and schema compliance.
- Deploy on Render with health checks.
