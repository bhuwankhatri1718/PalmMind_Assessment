
from qdrant_client import QdrantClient

from app.core.config import settings


api_key = (
    settings.qdrant_api_key.get_secret_value()
    if settings.qdrant_api_key
    else None
)

if api_key == "":
    api_key = None


qdrant_client = QdrantClient(
    url=settings.qdrant_url,
    api_key=api_key,
    timeout=10,
)


def get_qdrant_client() -> QdrantClient:
    return qdrant_client
