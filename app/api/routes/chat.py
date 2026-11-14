
from fastapi import APIRouter, HTTPException

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.rag_service import answer_question


router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    """Handle conversational RAG requests."""

    try:
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
