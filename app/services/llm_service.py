
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
