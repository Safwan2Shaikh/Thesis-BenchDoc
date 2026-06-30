"""
chunk_md_retriever.py

Retrieves relevant knowledge chunks
from Chunks_NLP folder.
"""

from pathlib import Path
from rapidfuzz import fuzz
from thesis.infra.paths import knowledge_base_dir

def _resolve_kb_folder() -> Path:
    base = knowledge_base_dir()
    candidate_new = base / "Chunks_NLP"
    candidate_legacy = base / "Chucks_NLP"
    if candidate_new.exists():
        return candidate_new
    return candidate_legacy


KB_FOLDER = _resolve_kb_folder()

TOP_K = 5
MIN_SCORE = 40


def load_chunks():

    chunks = []

    for file in KB_FOLDER.rglob("*.md"):

        try:

            content = file.read_text(
                encoding="utf-8"
            )

            chunks.append({
                "file_name": file.name,
                "category": file.parent.name,
                "content": content
            })

        except Exception as e:

            print(
                f"Failed loading {file}: {e}"
            )

    return chunks


def retrieve_chunks(query):

    chunks = load_chunks()

    results = []

    query = query.lower()

    for chunk in chunks:

        text = chunk["content"].lower()

        score = (
            0.5 * fuzz.token_sort_ratio(
                query,
                text
            )
            +
            0.3 * fuzz.partial_ratio(
                query,
                text
            )
            +
            0.2 * fuzz.token_set_ratio(
                query,
                text
            )
        )

        results.append({
            "score": score,
            "file_name": chunk["file_name"],
            "category": chunk["category"],
            "content": chunk["content"]
        })

    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    filtered = [
        r
        for r in results
        if r["score"] >= MIN_SCORE
    ][:TOP_K]

    print("\n=== CHUNK RETRIEVAL ===")

    for item in filtered:

        print(
            f"{item['score']:.1f} | {item['file_name']}"
        )

    return filtered