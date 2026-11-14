
from datetime import date, datetime, time
from pydantic import BaseModel, ConfigDict, EmailStr


class BookingExtraction(BaseModel):
    """Partially collected booking information from the conversation."""

    booking_intent: bool = False
    full_name: str | None = None
    email: str | None = None
    interview_date: date | None = None
    interview_time: time | None = None


class BookingResponse(BaseModel):
    """Booking information returned after saving to the database."""

    id: int
    conversation_id: str
    full_name: str
    email: EmailStr
    interview_date: date
    interview_time: time
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
