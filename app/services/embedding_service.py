
from sentence_transformers import SentenceTransformer

from app.core.config import settings


model = SentenceTransformer(settings.embedding_model)


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """Convert text chunks into numerical embeddings."""

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    return embeddings.tolist()
