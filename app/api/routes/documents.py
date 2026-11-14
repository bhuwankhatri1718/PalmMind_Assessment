
from pathlib import Path
from typing import Literal
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.postgres import get_db
from app.models.document import Document
from app.schemas.document import DocumentResponse
from app.services.chunker import fixed_size_chunking, recursive_chunking
from app.services.embedding_service import generate_embeddings
from app.services.text_extractor import extract_text
from app.services.vector_store import create_collection, store_vectors


router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", response_model=DocumentResponse)
def upload_document(
    file: UploadFile = File(...),
    chunking_strategy: Literal["fixed_size", "recursive"] = Query(
        default="recursive"
    ),
    db: Session = Depends(get_db),
):
    # Validate file type
    extension = Path(file.filename or "").suffix.lower()

    if extension not in [".pdf", ".txt"]:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and TXT files are supported.",
        )

    # Read and validate file size
    file_content = file.file.read(settings.max_upload_size_mb * 1024 * 1024 + 1)

    if len(file_content) > settings.max_upload_size_mb * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="File size exceeds the allowed limit.",
        )

    # Save uploaded file
    settings.upload_dir.mkdir(parents=True, exist_ok=True)

    file_path = settings.upload_dir / f"{uuid4().hex}{extension}"
    file_path.write_bytes(file_content)

    try:
        # Extract document text
        text = extract_text(file_path)

        # Split text into chunks
        if chunking_strategy == "fixed_size":
            chunks = fixed_size_chunking(text)
        else:
            chunks = recursive_chunking(text)

        # Generate embeddings
        embeddings = generate_embeddings(chunks)

        # Create Qdrant collection
        create_collection()

        # Save document metadata in PostgreSQL
        document = Document(
            filename=Path(file.filename or "document").name,
            file_type=extension,
            file_size=len(file_content),
            chunk_count=len(chunks),
        )

        db.add(document)
        db.flush()

        # Save chunks and embeddings in Qdrant
        store_vectors(
            document_id=document.id,
            chunks=chunks,
            embeddings=embeddings,
        )

        db.commit()
        db.refresh(document)

        return document

    except ValueError as error:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(error)) from error

    except Exception as error:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Document processing failed.",
        ) from error

    finally:
        file_path.unlink(missing_ok=True)
