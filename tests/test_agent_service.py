"""Tests for the AgentService and its message shaping."""

import os
from types import SimpleNamespace
import pytest  # type: ignore

from agent.service import (
    AgentService,
    _ensure_system,   # internal helper (ok to test: critical behavior)
    _clip_messages,   # internal helper (ensures guardrails work)
    SOCRATIC_SYSTEM,
)


# ---------- Initialization ----------

def test_agent_service_initialization_defaults():
    """Defaults should match our config and be overridable."""
    service = AgentService()
    # Default model comes from env OPENAI_MODEL (fallback in service code).
    # In tests, we assert against whatever the instance reports.
    assert isinstance(service.model, str) and len(service.model) > 0

def test_agent_service_initialization_custom_model():
    """Custom model should be respected."""
    custom_model = "gpt-4"
    service = AgentService(model=custom_model)
    assert service.model == custom_model


# ---------- Message shaping (no network) ----------

def test_ensure_system_injects_when_missing():
    """If no system message is provided, prepend ours (with optional context)."""
    msgs = [{"role": "user", "content": "hi"}]
    out = _ensure_system(msgs, context={"lesson": "Variables"})
    assert out[0]["role"] == "system"
    assert SOCRATIC_SYSTEM in out[0]["content"]
    assert "Context: lesson: Variables" in out[0]["content"]

def test_ensure_system_prepends_when_client_has_system():
    """Our system prompt should come first; client system stays second."""
    msgs = [
        {"role": "system", "content": "client system"},
        {"role": "user", "content": "hi"},
    ]
    out = _ensure_system(msgs, context=None)
    assert out[0]["role"] == "system"
    assert SOCRATIC_SYSTEM in out[0]["content"]
    # Ensure client's system is preserved (now second)
    assert out[1]["role"] == "system"
    assert out[1]["content"] == "client system"

def test_clip_messages_limits_turns_and_length():
    """Clip to last N messages and truncate overly long content."""
    long_text = "x" * 10_000
    msgs = [{"role": "user", "content": f"{i}:{long_text}"} for i in range(20)]
    clipped = _clip_messages(msgs)
    # Our helper should keep a tail (<= MAX_TURNS) and trim content length
    assert len(clipped) <= 12
    assert all(len(m["content"]) <= 4000 for m in clipped)


# ---------- get_response (mocked OpenAI) ----------

def test_get_response_returns_text_with_mock(monkeypatch):
    """Mock OpenAI call to ensure we return the assistant content."""
    # Create a fake OpenAI response
    fake_response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content="mocked reply"))]
    )

    # Monkeypatch the OpenAI client's chat.completions.create
    from agent import service as svc_module
    def fake_create(**kwargs):
        # Basic sanity on message shaping
        msgs = kwargs.get("messages", [])
        assert msgs and msgs[0]["role"] == "system"
        assert SOCRATIC_SYSTEM in msgs[0]["content"]
        return fake_response

    monkeypatch.setattr(svc_module.client.chat.completions, "create", fake_create)

    svc = AgentService()
    out = svc.get_response([{"role": "user", "content": "hello"}], user_id="u1", context={"lesson": "Loops"})
    assert out == "mocked reply"

def test_get_response_handles_openai_errors(monkeypatch):
    """If OpenAI raises, return a friendly fallback string."""
    from agent import service as svc_module

    def boom(**kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(svc_module.client.chat.completions, "create", boom)

    svc = AgentService()
    out = svc.get_response([{"role": "user", "content": "hello"}])
    assert isinstance(out, str)
    assert "try again" in out.lower()
