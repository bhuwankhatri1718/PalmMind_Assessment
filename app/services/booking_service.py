
from datetime import date, time
from sqlalchemy.orm import Session

from app.models.booking import Booking
from app.schemas.booking import BookingExtraction
from app.services.llm_service import extract_booking_details
from app.services.memory_service import get_chat_history, save_chat_message


def handle_booking(
    conversation_id: str,
    question: str,
    db: Session,
) -> str:
    """Collect interview details and save a completed booking."""

    history = get_chat_history(conversation_id)

    conversation = "\n".join(
        f"{message['role']}: {message['content']}"
        for message in history[-10:]
    )

    conversation += f"\nuser: {question}"

    details: BookingExtraction = extract_booking_details(conversation)

    if not details.booking_intent:
        return ""

    if not details.full_name:
        answer = "Sure! May I have your full name?"
    elif not details.email:
        answer = "Thanks! What is your email address?"
    elif not details.interview_date:
        answer = "What date would you prefer for your interview? Please provide the date in YYYY-MM-DD format."
    elif not details.interview_time:
        answer = "What time would you prefer for your interview?"
    else:
        existing_booking = db.query(Booking).filter(
            Booking.conversation_id == conversation_id
        ).first()

        if existing_booking:
            return "An interview booking already exists for this conversation."

        booking = Booking(
            conversation_id=conversation_id,
            full_name=details.full_name,
            email=details.email,
            interview_date=details.interview_date,
            interview_time=details.interview_time,
        )

        db.add(booking)
        db.commit()
        db.refresh(booking)

        answer = (
            f"Your interview booking has been saved successfully!\n"
            f"Name: {booking.full_name}\n"
            f"Email: {booking.email}\n"
            f"Date: {booking.interview_date}\n"
            f"Time: {booking.interview_time}"
        )

    save_chat_message(conversation_id, "user", question)
    save_chat_message(conversation_id, "assistant", answer)

    return answer
