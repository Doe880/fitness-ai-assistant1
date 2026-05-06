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


def extract_title(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("ТЕМА:"):
            return line.replace("ТЕМА:", "").strip()
    return "Без названия"


def extract_category(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("КАТЕГОРИЯ:"):
            return line.replace("КАТЕГОРИЯ:", "").strip()
    return "без категории"


def keyword_score(query: str, text: str) -> float:
    query_words = [
        word.strip(".,!?;:()[]{}\"'").lower().replace("ё", "е")
        for word in query.split()
        if len(word.strip()) > 2
    ]

    text_lower = text.lower().replace("ё", "е")

    if not query_words:
        return 0.0

    matches = sum(1 for word in query_words if word in text_lower)

    return matches / len(query_words)


def detect_category(query: str) -> str | None:
    q = query.lower()

    nutrition_words = [
        "еда", "питание", "белок", "углеводы", "протеин",
        "креатин", "калории", "масса", "вес", "спортпит"
    ]

    training_words = [
        "тренировка", "упражнение", "грудь", "спина", "ноги",
        "плечи", "руки", "пресс", "зал", "дома"
    ]

    recovery_words = [
        "восстановление", "сон", "усталость", "перетренированность",
        "болят", "отдых"
    ]

    if any(word in q for word in nutrition_words):
        return "питание"

    if any(word in q for word in training_words):
        return "тренировки"

    if any(word in q for word in recovery_words):
        return "восстановление"

    return None


def semantic_search(query: str, limit: int = 5) -> list[dict]:
    index = load_index()
    query_embedding = create_embedding(query)

    category_hint = detect_category(query)

    scored = []

    for item in index:
        text = item["text"]

        semantic = cosine_similarity(query_embedding, item["embedding"])
        keyword = keyword_score(query, text)

        category = extract_category(text)

        category_bonus = 0.0
        if category_hint and category_hint == category:
            category_bonus = 0.08

        final_score = semantic * 0.75 + keyword * 0.25 + category_bonus

        scored.append(
            {
                "id": item["id"],
                "title": extract_title(text),
                "category": category,
                "text": text,
                "semantic_score": semantic,
                "keyword_score": keyword,
                "score": final_score
            }
        )

    scored.sort(key=lambda item: item["score"], reverse=True)

    return scored[:limit]