"""API routes for the Gcode Academy Agent."""
from fastapi import APIRouter, HTTPException

from agent.service import AgentService
from api.models import ChatRequest, ChatResponse, Message

# Create router
router = APIRouter()

# Initialize agent service
agent_service = AgentService()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Process a chat request and return a response.

    Args:
        request: The chat request containing messages and optional context

    Returns:
        A response containing the assistant's message
    """
    try:
        # Convert Pydantic models to dictionaries for the OpenAI API
        messages_dict = [{"role": msg.role, "content": msg.content} for msg in request.messages]

        # Get response from agent service
        response_text = agent_service.get_response(
            messages=messages_dict,
            user_id=request.user_id,
            context=request.context
        )

        # Return the response
        return ChatResponse(
            message=Message(role="assistant", content=response_text)
        )

    except Exception as e:
        # Log the error
        print(f"Error processing chat request: {e}")

        # Raise HTTP exception
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your request"
        ) from e
