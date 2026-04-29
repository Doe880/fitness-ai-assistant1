from pathlib import Path


KNOWLEDGE_FILE = Path(__file__).parent / "knowledge.txt"


def load_knowledge_text() -> str:
    return KNOWLEDGE_FILE.read_text(encoding="utf-8")


def split_into_chunks(text: str) -> list[str]:
    chunks = []

    for part in text.split("\n\n"):
        cleaned = part.strip()
        if cleaned:
            chunks.append(cleaned)

    return chunks


def get_knowledge_chunks() -> list[dict]:
    """
    Возвращает список документов:
    [
      {"id": 1, "text": "..."},
      {"id": 2, "text": "..."}
    ]
    """
    text = load_knowledge_text()
    chunks = split_into_chunks(text)

    return [
        {
            "id": index + 1,
            "text": chunk
        }
        for index, chunk in enumerate(chunks)
    ]