
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.core.config import settings
from app.db.postgres import Base, engine
from app.db.qdrant import qdrant_client
from app.db.redis import redis_client
from app.models.document import Document
from app.api.routes.documents import router as documents_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create database tables
    Base.metadata.create_all(bind=engine)

    # Test PostgreSQL connection
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    print("PostgreSQL connected.")

    # Test Redis connection
    redis_client.ping()
    print("Redis connected.")

    # Test Qdrant connection
    qdrant_client.get_collections()
    print("Qdrant connected.")

    yield

    # Close connections
    redis_client.close()
    qdrant_client.close()
    engine.dispose()


app = FastAPI(
    title=settings.app_name,
    description="Document ingestion, conversational RAG and interview booking backend.",
    version="1.0.0",
    lifespan=lifespan,
)

# Register document ingestion API
app.include_router(documents_router)


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "application": settings.app_name,
    }
