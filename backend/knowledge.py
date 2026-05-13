from pathlib import Path

import yaml


KNOWLEDGE_FILE = Path(__file__).parent / "knowledge.yaml"


def load_knowledge_items() -> list[dict]:
    with open(KNOWLEDGE_FILE, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    if not data:
        return []

    return data


def item_to_text(item: dict) -> str:
    """
    Превращаем YAML-объект в текст для embeddings.
    Чем больше полезных полей попадет сюда, тем лучше semantic search.
    """
    title = item.get("title", "")
    category = item.get("category", "")
    item_type = item.get("type", "")
    muscle_groups = ", ".join(item.get("muscle_groups", []))
    equipment = ", ".join(item.get("equipment", []))
    level = ", ".join(item.get("level", []))
    text = item.get("text", "")

    return (
        f"ТЕМА: {title}\n"
        f"КАТЕГОРИЯ: {category}\n"
        f"ТИП: {item_type}\n"
        f"ГРУППЫ МЫШЦ: {muscle_groups}\n"
        f"ОБОРУДОВАНИЕ: {equipment}\n"
        f"УРОВЕНЬ: {level}\n"
        f"ТЕКСТ:\n{text}"
    )


def get_knowledge_chunks() -> list[dict]:
    items = load_knowledge_items()

    chunks = []

    for index, item in enumerate(items):
        chunks.append(
            {
                "id": item.get("id", index + 1),
                "text": item_to_text(item),
                "metadata": item
            }
        )

    return chunks