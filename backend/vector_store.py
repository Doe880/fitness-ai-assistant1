import json
from pathlib import Path

import numpy as np


INDEX_FILE = Path(__file__).parent / "fitness_index.json"


def load_index() -> list[dict]:
    """
    Загружает векторный индекс из fitness_index.json.
    """
    if not INDEX_FILE.exists():
        raise FileNotFoundError(
            f"Index file not found: {INDEX_FILE}. "
            f"Run build_index.py first."
        )

    with open(INDEX_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


# Загружаем индекс один раз при старте приложения
INDEX = load_index()


def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    """
    Косинусное сходство между двумя векторами.
    """
    a = np.array(vec1)
    b = np.array(vec2)

    denominator = np.linalg.norm(a) * np.linalg.norm(b)

    if denominator == 0:
        return 0.0

    return float(np.dot(a, b) / denominator)


def extract_title(text: str) -> str:
    """
    Fallback: извлекает заголовок из текстового блока,
    если metadata отсутствует.
    """
    for line in text.splitlines():
        if line.startswith("ТЕМА:"):
            return line.replace("ТЕМА:", "").strip()

    return "Без названия"


def extract_category(text: str) -> str:
    """
    Fallback: извлекает категорию из текстового блока,
    если metadata отсутствует.
    """
    for line in text.splitlines():
        if line.startswith("КАТЕГОРИЯ:"):
            return line.replace("КАТЕГОРИЯ:", "").strip()

    return "без категории"


def semantic_search(
    query: str,
    limit: int = 5
) -> list[dict]:
    """
    Выполняет semantic search по fitness_index.json.

    Возвращает список словарей:
    {
        "id": ...,
        "text": ...,
        "title": ...,
        "category": ...,
        "metadata": {...},
        "score": ...
    }
    """
    # Импорт внутри функции, чтобы избежать циклических импортов
    from embeddings import create_embedding

    query_embedding = create_embedding(query)

    results = []

    for item in INDEX:
        score = cosine_similarity(
            query_embedding,
            item["embedding"]
        )

        text = item.get("text", "")
        metadata = item.get("metadata", {})

        results.append(
            {
                "id": item.get("id"),
                "text": text,
                "title": metadata.get(
                    "title",
                    extract_title(text)
                ),
                "category": metadata.get(
                    "category",
                    extract_category(text)
                ),
                "metadata": metadata,
                "score": score,
            }
        )

    # Сортировка по убыванию релевантности
    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return results[:limit]