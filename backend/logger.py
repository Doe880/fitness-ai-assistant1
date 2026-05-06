import json
from datetime import datetime
from pathlib import Path


LOG_FILE = Path(__file__).parent / "query_logs.jsonl"


def log_query(query: str, answer: str, sources: list[dict]) -> None:
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "query": query,
        "answer": answer,
        "sources": sources
    }

    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(json.dumps(record, ensure_ascii=False) + "\n")