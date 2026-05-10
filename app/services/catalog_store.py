import json
import os
from pathlib import Path

from langchain_core.documents import Document
from langchain_chroma import Chroma


def _arr_to_embedding_vector(arr) -> list[float]:
    """Turn HF / local encoder output into a single 1D float vector."""
    import numpy as np

    a = np.asarray(arr, dtype=np.float64)
    # Token-matrix outputs: (n_tokens, dim) -> mean pool
    if a.ndim == 2:
        a = np.mean(a, axis=0)
    return a.astype(float).flatten().tolist()


class HuggingFaceAPIEmbeddings:
    """
    Uses huggingface_hub.InferenceClient so the correct Inference API / provider
    URL is used (raw api-inference.huggingface.co URLs often 404 now).
    """

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        api_key: str | None = None,
    ) -> None:
        from huggingface_hub import InferenceClient

        self.model_name = model_name
        self.api_key = api_key or os.getenv("HF_API_KEY") or os.getenv("HUGGINGFACE_API_KEY") or os.getenv("HF_TOKEN")
        if not self.api_key:
            raise ValueError(
                "Hugging Face API token is required. Set HF_API_KEY in .env (or HUGGINGFACE_API_KEY / HF_TOKEN)."
            )
        self._client = InferenceClient(token=self.api_key)
        self._batch_size = max(1, int(os.getenv("HF_EMBED_BATCH_SIZE", "24")))

    def _post(self, inputs: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for text in inputs:
            arr = self._client.feature_extraction(text, model=self.model_name)
            vectors.append(_arr_to_embedding_vector(arr))
        return vectors

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        out: list[list[float]] = []
        for start in range(0, len(texts), self._batch_size):
            chunk = texts[start : start + self._batch_size]
            out.extend(self._post(chunk))
        return out

    def embed_query(self, text: str) -> list[float]:
        return self._post([text])[0]


class LocalSentenceTransformerEmbeddings:
    """Runs MiniLM locally (no Inference API); best for bulk ingest of large catalogs."""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2") -> None:
        from sentence_transformers import SentenceTransformer

        self.model_name = model_name
        self._model = SentenceTransformer(model_name)
        self._batch_size = max(1, int(os.getenv("HF_EMBED_BATCH_SIZE", "64")))

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        out: list[list[float]] = []
        for start in range(0, len(texts), self._batch_size):
            chunk = texts[start : start + self._batch_size]
            enc = self._model.encode(chunk, show_progress_bar=False, convert_to_numpy=True)
            for row in enc:
                out.append(_arr_to_embedding_vector(row))
        return out

    def embed_query(self, text: str) -> list[float]:
        enc = self._model.encode([text], show_progress_bar=False, convert_to_numpy=True)[0]
        return _arr_to_embedding_vector(enc)


def build_embedding_function():
    backend = (os.getenv("HF_EMBED_BACKEND") or "api").strip().lower()
    model = os.getenv("HF_EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    if backend in ("local", "cpu", "offline"):
        return LocalSentenceTransformerEmbeddings(model_name=model)
    return HuggingFaceAPIEmbeddings(model_name=model)


def sanitize_chroma_metadata(metadata: dict) -> dict:
    """
    Chroma rejects empty Python lists as metadata values.
    Omit those keys (and coerce other types Chroma accepts).
    """
    out: dict = {}
    for key, val in metadata.items():
        if val is None:
            continue
        if isinstance(val, (bool, int, float)):
            out[key] = val
            continue
        if isinstance(val, str):
            out[key] = val
            continue
        if isinstance(val, list):
            if not val:
                continue
            out[key] = [str(x) for x in val]
            continue
        if isinstance(val, dict):
            out[key] = json.dumps(val, ensure_ascii=False)
            continue
        out[key] = str(val)
    return out


def build_document(item: dict) -> Document:
    """Build RAG chunk + Chroma-safe metadata (SHL dataset uses link/keys/job_levels/languages…)."""
    raw = dict(item)
    skill_tags = raw.get("skills_measured") or raw.get("keys") or []
    if isinstance(skill_tags, str):
        skill_text = skill_tags
    else:
        skill_text = ", ".join(str(x) for x in skill_tags)

    job_levels = raw.get("job_levels") or []
    job_levels_text = ", ".join(str(x) for x in job_levels) if isinstance(job_levels, list) else str(job_levels)

    langs = raw.get("languages") or []
    langs_text = ", ".join(str(x) for x in langs) if isinstance(langs, list) else str(langs)

    url = (raw.get("url") or raw.get("link") or "").strip()
    catalog_id = raw.get("entity_id") or raw.get("id") or ""

    content = (
        f"Assessment: {raw.get('name', '')}\n"
        f"ID: {catalog_id}\n"
        f"Description: {raw.get('description', '')}\n"
        f"Assessment types / keys: {skill_text}\n"
        f"Duration: {raw.get('duration', '') or raw.get('duration_raw', '')}\n"
        f"Job levels: {job_levels_text}\n"
        f"Languages: {langs_text}\n"
        f"Remote: {raw.get('remote', '')}  Adaptive: {raw.get('adaptive', '')}\n"
        f"URL: {url}"
    )
    meta = sanitize_chroma_metadata(raw)
    if url:
        meta.setdefault("url", url)
    return Document(page_content=content, metadata=meta)


def load_catalog(path: str) -> list[dict]:
    with Path(path).open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("Catalog JSON must be a list of assessment objects.")
    return data


def load_vector_store(persist_directory: str) -> Chroma:
    return Chroma(
        collection_name="shl_assessments",
        embedding_function=build_embedding_function(),
        persist_directory=persist_directory,
    )
