import json
from pathlib import Path

import numpy as np

from embeddings import create_embedding


INDEX_FILE = Path(__file__).parent / "fitness_index.json"


def load_index() -> list[dict]:
    if not INDEX_FILE.exists():
        raise FileNotFoundError(
            "fitness_index.json не найден. Сначала запусти: python build_index.py"
        )

    return json.loads(INDEX_FILE.read_text(encoding="utf-8"))


def cosine_similarity(a: list[float], b: list[float]) -> float:
    vec_a = np.array(a)
    vec_b = np.array(b)

    denominator = np.linalg.norm(vec_a) * np.linalg.norm(vec_b)

    if denominator == 0:
        return 0.0

    return float(np.dot(vec_a, vec_b) / denominator)


def semantic_search(query: str, limit: int = 5) -> list[dict]:
    """
    Семантический поиск:
    1. создаем embedding запроса
    2. сравниваем с embedding каждого чанка
    3. возвращаем самые похожие
    """
    index = load_index()
    query_embedding = create_embedding(query)

    scored = []

    for item in index:
        score = cosine_similarity(query_embedding, item["embedding"])

        scored.append(
            {
                "id": item["id"],
                "text": item["text"],
                "score": score
            }
        )

    scored.sort(key=lambda item: item["score"], reverse=True)

    return scored[:limit]