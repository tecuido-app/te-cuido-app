import os

# Must be set before any agent imports so module-level wiring uses mocks
os.environ.setdefault("USE_MOCK_SOLANA", "true")
os.environ.setdefault("USE_MQTT", "false")
os.environ.setdefault("GEMINI_API_KEY", "")
os.environ.setdefault("TELEGRAM_BOT_TOKEN", "")

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def reset_state():
    from agent.state import state
    state.status = "ok"
    state.last_vitals = None
    state.active_event = None
    state.history.clear()
    state.recent_vitals.clear()
    state.wellbeing_confirmed = False
    yield
    state.status = "ok"
    state.last_vitals = None
    state.active_event = None
    state.history.clear()
    state.recent_vitals.clear()
    state.wellbeing_confirmed = False


@pytest.fixture
def client():
    from agent.api import app
    with TestClient(app) as c:
        yield c
