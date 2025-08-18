"""API data models for requests and responses."""
from typing import Any

from pydantic import BaseModel, Field # type: ignore


class Message(BaseModel):
    """Model for a chat message."""

    role: str = Field(
        ...,
        description="The role of the message sender (system, user, or assistant)"
    )
    content: str = Field(..., description="The content of the message")


class ChatRequest(BaseModel):
    """Model for chat requests."""

    messages: list[Message] = Field(
        ...,
        description="List of previous messages in the conversation"
    )
    user_id: str | None = Field(None, description="Optional user identifier")
    context: dict[str, Any] | None = Field(
        None, description="Optional context information (e.g., current lesson)"
    )


class ChatResponse(BaseModel):
    """Model for chat responses."""

    message: Message = Field(..., description="The assistant's response message")
