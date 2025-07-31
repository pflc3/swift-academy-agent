"""Tests for the agent service."""
import os
import pytest
from agent.service import AgentService


def test_agent_service_initialization():
    """Test that the agent service initializes correctly."""
    service = AgentService()
    assert service.model == "gpt-3.5-turbo"

    custom_model = "gpt-4"
    service = AgentService(model=custom_model)
    assert service.model == custom_model


# Skip this test if no API key is available
@pytest.mark.skipif(
    "OPENAI_API_KEY" not in os.environ, 
    reason="OpenAI API key not available"
)
def test_get_response():
    """Test getting a response from the agent."""
    service = AgentService()
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Say hello!"}
    ]
    
    response = service.get_response(messages)
    assert isinstance(response, str)
    assert len(response) > 0
