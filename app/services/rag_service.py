
from app.services.embedding_service import generate_embeddings
from app.services.vector_store import search_vectors
from app.services.llm_service import generate_response
from app.services.memory_service import (
    get_chat_history,
    save_chat_message,
)


def answer_question(
    question: str,
    conversation_id: str,
) -> str:
    """Answer questions using document retrieval and chat history."""

    # Retrieve previous conversation messages
    history = get_chat_history(conversation_id)

    # Convert the question into an embedding
    query_embedding = generate_embeddings([question])[0]

    # Retrieve relevant document chunks
    relevant_chunks = search_vectors(query_embedding)

    if not relevant_chunks:
        answer = (
            "I could not find relevant information "
            "in the uploaded documents."
        )
    else:
        context = "\n\n".join(relevant_chunks)

        # Format previous conversation history
        conversation_history = "\n".join(
            f"{message['role']}: {message['content']}"
            for message in history[-10:]
        )

        prompt = f"""
You are a helpful document assistant.

Use the provided document context and conversation history
to answer the user's question.

Answer using the document context.
If the answer is not available in the context,
clearly say that you could not find the information.

Conversation History:
{conversation_history}

Document Context:
{context}

Current Question:
{question}

Answer:
"""

        answer = generate_response(prompt)

    # Save the new messages in Redis
    save_chat_message(conversation_id, "user", question)
    save_chat_message(conversation_id, "assistant", answer)

    return answer
