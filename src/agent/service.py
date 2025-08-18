"""
Service layer for handling OpenAI chat completions.

Key responsibilities:
- Injects a consistent "Code Coach" system prompt (Socratic, 4-step style).
- Clips conversation history and message size to reduce cost and noise.
- Merges optional client context (e.g., lesson info).
- Wraps API calls and returns a safe, single assistant message string.
"""

import os
from typing import Any

from dotenv import load_dotenv  # type: ignore
from openai import OpenAI  # type: ignore

# Load environment variables from .env if present
load_dotenv()

# Get OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

# Model & generation defaults (tunable without code changes)
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
DEFAULT_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
DEFAULT_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "900"))

# OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Standard tutoring behavior — always injected as the first system message
SOCRATIC_SYSTEM = (
    "You are Code Coach. Teach Swift/SwiftUI/iOS to beginners. "
    "Be concise, friendly, and avoid markdown formatting. "
    "Use a 4-step method: 1) Understand 2) Plan 3) Write 4) Review. "
    "Keep examples short and readable for a phone screen."
)

# Guardrails for cost, performance, and stability
MAX_TURNS = 12              # keep only the last 12 conversation turns
MAX_CONTENT_CHARS = 4000    # clip any single message to 4000 characters


def _clip_messages(messages: list[dict[str, str]]) -> list[dict[str, str]]:
    """
    Reduce message list size.

    Keep only the last N turns & truncate overly long message contents.
    """
    tail = messages[-MAX_TURNS:]
    for m in tail:
        content = m.get("content", "")
        if len(content) > MAX_CONTENT_CHARS:
            m["content"] = content[:MAX_CONTENT_CHARS]
    return tail


def _ensure_system(messages: list[dict[str, str]],
                   context: dict[str, Any] | None) -> list[dict[str, str]]:
    """
    Guarantee that our system prompt is the first message.

    If context is provided, append it inline for extra guidance.
    If the client already provided a system prompt, we still prepend ours.
    """
    system = SOCRATIC_SYSTEM
    if context:
        ctx_str = ", ".join(f"{k}: {v}" for k, v in context.items() if v)
        if ctx_str:
            system += f"\nContext: {ctx_str}"

    if not messages or messages[0].get("role") != "system":
        return [{"role": "system", "content": system}] + messages

    # Always prepend our system message, but keep the client's system (if any) behind it
    return [{"role": "system", "content": system}] + messages


class AgentService:
    """Encapsulates all interactions with the OpenAI API."""

    def __init__(self, model: str = DEFAULT_MODEL):
        """
        Initialize the agent service.

        Args:
            model: The OpenAI model to use
        """
        self.model = model

    def get_response(
        self,
        messages: list[dict[str, str]],
        user_id: str | None = None,
        context: dict[str, Any] | None = None
    ) -> str:
        """
        Main entrypoint: clean inputs, call OpenAI, and return assistant text.

        Frontend should send only raw conversation turns.
        Backend owns tutoring style, guardrails, and context shaping.

        Args:
            messages: List of message objects with 'role' and 'content'
            user_id: Optional user identifier
            context: Optional context information (e.g., current lesson)

        Returns:
            The assistant's response text
        """
        try:
            # Log request details if needed
            if user_id:
                print(f"[agent] handling user_id={user_id}")

            # Clip and ensure system prompt
            msgs = _clip_messages(messages)
            msgs = _ensure_system(msgs, context)

            # Call OpenAI API
            response = client.chat.completions.create(
                model=self.model,
                messages=msgs,
                temperature=DEFAULT_TEMPERATURE,
                max_tokens=DEFAULT_MAX_TOKENS,
            )

            return response.choices[0].message.content or ""

        except Exception as e:
            # Fail safe: never leak raw errors to the student
            print(f"[agent] OpenAI error: {e}")
            return "I'm having trouble responding right now. Please try again in a moment."
