
import json

from app.db.redis import redis_client


def get_chat_history(conversation_id: str) -> list[dict[str, str]]:
    """Retrieve previous messages for a conversation."""

    key = f"chat:{conversation_id}"

    messages = redis_client.lrange(key, 0, -1)

    return [json.loads(message) for message in messages]


def save_chat_message(
    conversation_id: str,
    role: str,
    content: str,
) -> None:
    """Save a user or assistant message in Redis."""

    key = f"chat:{conversation_id}"

    message = {
        "role": role,
        "content": content,
    }

    redis_client.rpush(key, json.dumps(message))
