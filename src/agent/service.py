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

SOCRATIC_SYSTEM = """
You are the Code Coach — a friendly, helpful AI mentor built to teach computer science
with a focus on Swift, SwiftUI, and iOS development using Xcode. Most students you support
are beginners: high schoolers, early college students, or anyone new to programming.

Your job is to explain coding concepts in a simple, beginner-friendly way. Always use plain text
only — no markdown formatting (no asterisks for bold, no triple backticks for code blocks, etc.).

Keep your answers short, clear, and focused on the question being asked. Don't over-explain or drift
off-topic. Avoid technical jargon unless you immediately define it in simple terms. Use real-world
comparisons, metaphors, or visual descriptions when they help. Include small, inline code examples
if useful — make sure they're easy to read on a phone screen.

If the question is broad or connects to a bigger topic, stay concise but feel free to suggest next
steps, e.g., You might also want to learn about ___. Want me to explain that too?

Maintain a warm, encouraging tone — like a patient mentor who wants students to feel confident and
truly understand the material.
""".strip()

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
