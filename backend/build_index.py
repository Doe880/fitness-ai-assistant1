import json
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()  # важно ДО импорта embeddings

from embeddings import create_embeddings_batch
from knowledge import get_knowledge_chunks


INDEX_FILE = Path(__file__).parent / "fitness_index.json"


def build_index() -> None:
    chunks = get_knowledge_chunks()

    texts = [chunk["text"] for chunk in chunks]
    embeddings = create_embeddings_batch(texts)

    index = []

    for chunk, embedding in zip(chunks, embeddings):
        index.append(
            {
                "id": chunk["id"],
                "text": chunk["text"],
                "embedding": embedding
            }
        )

    INDEX_FILE.write_text(
        json.dumps(index, ensure_ascii=False),
        encoding="utf-8"
    )

    print(f"Index built: {len(index)} chunks saved to {INDEX_FILE}")


if __name__ == "__main__":
    build_index()