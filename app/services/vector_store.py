
from uuid import uuid4
from qdrant_client.models import SearchParams

from qdrant_client.models import Distance, PointStruct, VectorParams

from app.core.config import settings
from app.db.qdrant import qdrant_client


def create_collection() -> None:
    """Create the Qdrant collection if it does not exist."""

    if not qdrant_client.collection_exists(settings.qdrant_collection):
        qdrant_client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=VectorParams(
                size=settings.embedding_dimension,
                distance=Distance.COSINE,
            ),
        )


def store_vectors(
    document_id: int,
    chunks: list[str],
    embeddings: list[list[float]],
) -> None:
    """Store text chunks and embeddings in Qdrant."""

    points = []

    for index, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        points.append(
            PointStruct(
                id=str(uuid4()),
                vector=embedding,
                payload={
                    "document_id": document_id,
                    "chunk_index": index,
                    "text": chunk,
                },
            )
        )

    if points:
        qdrant_client.upsert(
            collection_name=settings.qdrant_collection,
            points=points,
        )



def search_vectors(
    query_embedding: list[float],
    limit: int = 5,
) -> list[str]:
    """Retrieve the most relevant document chunks from Qdrant."""

    results = qdrant_client.query_points(
        collection_name=settings.qdrant_collection,
        query=query_embedding,
        limit=limit,
        with_payload=True,
    ).points

    chunks = []

    for result in results:
        if result.payload and "text" in result.payload:
            chunks.append(result.payload["text"])

    return chunks
