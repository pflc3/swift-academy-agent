"""API data models for chat requests and responses."""

from typing import Any

from pydantic import BaseModel, Field  # type: ignore


class Message(BaseModel):
    """Represents a single chat message in role/content form."""

    role: str = Field(..., description="system, user, or assistant")
    content: str = Field(..., description="message text")


class ChatRequest(BaseModel):
    """
    Request body for /chat.

    messages: conversation so far
    user_id: optional client identifier
    context: optional domain/lesson info for shaping responses
    """

    messages: list[Message] = Field(..., description="conversation so far")
    user_id: str | None = Field(None, description="optional user identifier")
    context: dict[str, Any] | None = Field(None, description="optional context (e.g., lesson)")


class ChatResponse(BaseModel):
    """Response body containing a single assistant message."""

    message: Message = Field(..., description="assistant reply")
