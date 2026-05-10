import sys
from pathlib import Path

# Running `python scripts/ingest.py` puts `scripts/` on sys.path first, so `app` must be rooted at project dir.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from dotenv import load_dotenv

load_dotenv(_PROJECT_ROOT / ".env")

from langchain_chroma import Chroma

from app.services.catalog_store import build_document, build_embedding_function, load_catalog


def ingest(catalog_path: str = "data/shl_catalog.json", db_path: str = "data/chroma_db") -> None:
    items = load_catalog(catalog_path)
    docs = [build_document(i) for i in items]
    ids = [f"assessment-{idx}" for idx in range(len(docs))]

    Path(db_path).mkdir(parents=True, exist_ok=True)
    embed_fn = build_embedding_function()
    vector_store = Chroma(
        collection_name="shl_assessments",
        embedding_function=embed_fn,
        persist_directory=db_path,
    )
    vector_store.delete_collection()
    vector_store = Chroma(
        collection_name="shl_assessments",
        embedding_function=embed_fn,
        persist_directory=db_path,
    )
    vector_store.add_documents(docs, ids=ids)
    print(f"Ingested {len(docs)} documents into {db_path}")


if __name__ == "__main__":
    ingest()
