from app.schemas.booking import BookingExtraction
from groq import Groq

from app.core.config import settings


client = Groq(
    api_key=settings.groq_api_key.get_secret_value()
)


def generate_response(prompt: str) -> str:
    """Generate an answer using the Groq language model."""

    response = client.chat.completions.create(
        model=settings.groq_model,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        temperature=0,
    )

    return response.choices[0].message.content or ""




def extract_booking_details(conversation: str) -> BookingExtraction:
    """Extract interview booking details from conversation history."""

    prompt = f"""
You are an information extraction assistant.

Extract interview booking information from the conversation below.

Return a JSON object with exactly these fields:
- booking_intent: boolean
- full_name: string or null
- email: string or null
- interview_date: date in YYYY-MM-DD format or null
- interview_time: time in HH:MM:SS 24-hour format or null

Rules:
1. Set booking_intent to true when the user wants to book an interview.
2. Extract only information explicitly provided by the user.
3. Never invent or assume missing information.
4. Use null for information that is missing or unclear.
5. Convert clear dates and times into the required formats.
6. If the user has not expressed booking intent, set booking_intent to false.

Conversation:
{conversation}
"""

    response = client.chat.completions.create(
        model=settings.groq_model,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0,
        response_format={"type": "json_object"},
    )

    result = response.choices[0].message.content or "{}"

    return BookingExtraction.model_validate_json(result)

