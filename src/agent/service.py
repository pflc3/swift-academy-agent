"""Service layer for interacting with OpenAI."""
import os
from typing import Any

from dotenv import load_dotenv # type: ignore
from openai import OpenAI # type: ignore

# Load environment variables
load_dotenv()

# Get OpenAI API key from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Default model to use
DEFAULT_MODEL = "gpt-3.5-turbo"


class AgentService:
    """Service for interacting with OpenAI's API."""

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
        Get a response from the OpenAI API.

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
                print(f"Processing request for user: {user_id}")

            # Add context to system message if provided
            if context and messages and messages[0]["role"] == "system":
                context_str = ", ".join(f"{k}: {v}" for k, v in context.items())
                messages[0]["content"] += f"\nContext: {context_str}"

            # Call OpenAI API
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1000,
            )

            # Return the assistant's message
            return response.choices[0].message.content

        except Exception as e:
            # Log the error
            print(f"Error calling OpenAI API: {e}")

            # Return a friendly error message
            return "I'm sorry, I'm having trouble connecting right now. Please try again later."
