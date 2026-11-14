
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.postgres import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.booking_service import handle_booking
from app.services.rag_service import answer_question


router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
) -> ChatResponse:
    """Handle conversational RAG and interview booking requests."""

    try:
        booking_answer = handle_booking(
            conversation_id=request.conversation_id,
            question=request.question,
            db=db,
        )

        if booking_answer:
            answer = booking_answer
        else:
            answer = answer_question(
                question=request.question,
                conversation_id=request.conversation_id,
            )

        return ChatResponse(
            conversation_id=request.conversation_id,
            answer=answer,
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate chat response.",
        ) from error
