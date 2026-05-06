from openai import OpenAI


EMBEDDING_MODEL = "text-embedding-3-small"

_embedding_cache: dict[str, list[float]] = {}


def get_client() -> OpenAI:
    return OpenAI()


def create_embedding(text: str) -> list[float]:
    normalized = text.strip().lower()

    if normalized in _embedding_cache:
        return _embedding_cache[normalized]

    client = get_client()

    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text
    )

    embedding = response.data[0].embedding
    _embedding_cache[normalized] = embedding

    return embedding


def create_embeddings_batch(texts: list[str]) -> list[list[float]]:
    client = get_client()

    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts
    )

    return [item.embedding for item in response.data]