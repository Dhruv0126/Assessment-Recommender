from langchain_chroma import Chroma


def retrieve_assessments(vector_store: Chroma, query: str, k: int = 10) -> list[dict]:
    docs = vector_store.similarity_search(query, k=k)
    return [d.metadata for d in docs]


def format_retrieved_context(items: list[dict]) -> str:
    blocks: list[str] = []
    for i, item in enumerate(items, start=1):
        blocks.append(
            "\n".join(
                [
                    f"[{i}] Name: {item.get('name', '')}",
                    f"URL: {item.get('url', '')}",
                    f"Type: {item.get('test_type', '')}",
                    f"Category: {item.get('category', '')}",
                    f"Duration: {item.get('duration', '')}",
                    f"Skills: {', '.join(item.get('skills_measured', []))}",
                    f"Description: {item.get('description', '')}",
                ]
            )
        )
    return "\n\n".join(blocks)
