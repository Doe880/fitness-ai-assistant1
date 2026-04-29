from openai import OpenAI


EMBEDDING_MODEL = "text-embedding-3-small"


def get_client() -> OpenAI:
    return OpenAI()


def create_embedding(text: str) -> list[float]:
    client = get_client()

    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text
    )

    return response.data[0].embedding


def create_embeddings_batch(texts: list[str]) -> list[list[float]]:
    client = get_client()

    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts
    )

    return [item.embedding for item in response.data]