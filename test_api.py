"""
Basic smoke tests for the Fitness AI Agent.

Run with:
    GEMINI_API_KEY=<your-key> python -m pytest test_api.py -v

These tests do NOT call the live Gemini API — they mock the client so
the suite runs offline and quickly.
"""
import sys
import os
import json
import types
import pytest

# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_fake_response(text: str):
    """Return a minimal object that looks like a Gemini GenerateContentResponse."""
    part = types.SimpleNamespace(text=text)
    content = types.SimpleNamespace(parts=[part])
    candidate = types.SimpleNamespace(content=content)
    return types.SimpleNamespace(candidates=[candidate])


def _patch_client(agent, text: str):
    """Replace agent._client with a fake that always returns `text`."""
    fake_models = types.SimpleNamespace(
        generate_content=lambda **kw: _make_fake_response(text)
    )
    agent._client = types.SimpleNamespace(models=fake_models)


# ── RouterAgent ───────────────────────────────────────────────────────────────

def test_router_returns_valid_category(monkeypatch):
    from agent.router import RouterAgent

    router = RouterAgent()
    _patch_client(router, "workout")

    result = router.run("How many push-ups should I do?")
    assert result in {"workout", "nutrition", "recovery", "both", "general", "plan"}


def test_router_falls_back_to_general_on_unknown(monkeypatch):
    from agent.router import RouterAgent

    router = RouterAgent()
    _patch_client(router, "something_unexpected")

    result = router.run("Hello there!")
    assert result == "general"


# ── WorkoutAgent ──────────────────────────────────────────────────────────────

def test_workout_agent_returns_string(monkeypatch):
    from agent.workout import WorkoutAgent

    agent = WorkoutAgent()
    _patch_client(agent, "Here is your workout plan: ...")

    result = agent.run("Give me a chest workout")
    assert isinstance(result, str)
    assert len(result) > 0


def test_workout_agent_reset_clears_memory(monkeypatch):
    from agent.workout import WorkoutAgent

    agent = WorkoutAgent()
    _patch_client(agent, "reply")
    agent.run("test")
    assert len(agent.memory) > 0
    agent.reset()
    assert agent.memory == []


# ── NutritionAgent ────────────────────────────────────────────────────────────

def test_nutrition_agent_returns_string(monkeypatch):
    from agent.nutrition import NutritionAgent

    agent = NutritionAgent()
    _patch_client(agent, "Here is your meal plan: ...")

    result = agent.run("What should I eat to lose weight?")
    assert isinstance(result, str)


def test_nutrition_agent_reset_clears_memory(monkeypatch):
    from agent.nutrition import NutritionAgent

    agent = NutritionAgent()
    _patch_client(agent, "reply")
    agent.run("test")
    assert len(agent.memory) > 0
    agent.reset()
    assert agent.memory == []


# ── RecoveryAgent ─────────────────────────────────────────────────────────────

def test_recovery_agent_returns_string(monkeypatch):
    from agent.recovery import RecoveryAgent

    agent = RecoveryAgent()
    _patch_client(agent, "Rest and stretch ...")

    result = agent.run("I'm really sore after leg day")
    assert isinstance(result, str)


# ── GeneralAgent ──────────────────────────────────────────────────────────────

def test_general_agent_chat_action(monkeypatch):
    from agent.general import GeneralAgent

    agent = GeneralAgent()
    _patch_client(agent, json.dumps({"action": "chat", "reply": "Hello! How can I help?"}))

    reply, action = agent.run("Hey!")
    assert action == "general"
    assert "Hello" in reply


def test_general_agent_reroute_action(monkeypatch):
    from agent.general import GeneralAgent

    agent = GeneralAgent()
    _patch_client(agent, json.dumps({"action": "reroute", "query": "Create a leg day workout plan."}))

    reply, action = agent.run("yeah do that")
    assert action == "reroute"
    assert "leg day" in reply.lower()


def test_general_agent_handles_bad_json(monkeypatch):
    from agent.general import GeneralAgent

    agent = GeneralAgent()
    _patch_client(agent, "This is not JSON at all.")

    reply, action = agent.run("something odd")
    # Should fall back gracefully
    assert action == "general"


# ── FullPackageAgent ──────────────────────────────────────────────────────────

def test_full_package_agent_returns_string(monkeypatch):
    from agent.full_package_agent import FullPackageAgent

    agent = FullPackageAgent()
    _patch_client(agent, "## Workout Plan\n...\n## Nutrition Plan\n...\n## Recovery Plan\n...")

    result = agent.run("Give me a complete weekly fitness plan")
    assert isinstance(result, str)
    assert "Workout" in result or "Plan" in result


# ── EmailAgent ────────────────────────────────────────────────────────────────

def test_email_agent_fails_gracefully_without_credentials():
    from agent.email_agent import EmailAgent

    # Clear env so no credentials are picked up
    os.environ.pop("GMAIL_USER", None)
    os.environ.pop("GMAIL_APP_PASSWORD", None)

    agent = EmailAgent()
    ok, msg = agent.send("test@example.com", "Subject", "Body")
    assert ok is False
    assert "credential" in msg.lower() or "missing" in msg.lower()


# ── AgentRouter integration ───────────────────────────────────────────────────

def test_agent_router_workout_route(monkeypatch):
    """End-to-end: router says 'workout', WorkoutAgent runs."""
    from main import AgentRouter

    router = AgentRouter()
    _patch_client(router.router, "workout")
    _patch_client(router.workout_agent, "Your workout plan is ...")

    reply, route = router.run("Give me a chest workout")
    assert route == "workout"
    assert isinstance(reply, str)


def test_agent_router_general_chat(monkeypatch):
    from main import AgentRouter

    router = AgentRouter()
    _patch_client(router.router, "general")
    _patch_client(
        router.general_agent,
        json.dumps({"action": "chat", "reply": "Hey! Ask me about fitness."})
    )

    reply, route = router.run("hello")
    assert route == "general"


def test_agent_router_reset_all(monkeypatch):
    from main import AgentRouter

    router = AgentRouter()
    # Populate memory on all stateful agents
    for agent in [router.workout_agent, router.nutrition_agent, router.recovery_agent]:
        _patch_client(agent, "reply")
        agent.run("test")

    router.reset_all()

    assert router.workout_agent.memory == []
    assert router.nutrition_agent.memory == []
    assert router.recovery_agent.memory == []
    assert router.general_agent.memory == []