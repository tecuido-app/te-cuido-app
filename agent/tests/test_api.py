import pytest


def test_root_redirects_to_docs(client):
    r = client.get("/", follow_redirects=False)
    assert r.status_code == 307
    assert "/docs" in r.headers["location"]


def test_health(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_status_initial_state(client):
    r = client.get("/api/status")
    assert r.status_code == 200
    d = r.json()
    assert d["status"] == "ok"
    assert "patient" in d
    assert d["vitals"] is None
    assert d["active_event"] is None
    assert d["history"] == []


def test_status_has_patient_info(client):
    r = client.get("/api/status")
    patient = r.json()["patient"]
    assert "name" in patient
    assert "age" in patient
    assert isinstance(patient["age"], int)


def test_wellbeing_sets_flag(client):
    r = client.post("/api/wellbeing")
    assert r.status_code == 200
    assert r.json()["ok"] is True


def test_simulate_low_hr(client):
    r = client.post("/api/simulate?event_type=low_hr")
    assert r.status_code == 200
    d = r.json()
    assert d["ok"] is True
    assert d["event_type"] == "LowHR"
    assert isinstance(d["value"], float)


def test_simulate_fall(client):
    r = client.post("/api/simulate?event_type=fall")
    assert r.status_code == 200
    assert r.json()["event_type"] == "Fall"


def test_simulate_low_spo2(client):
    r = client.post("/api/simulate?event_type=low_spo2")
    assert r.status_code == 200
    assert r.json()["event_type"] == "LowSpO2"


def test_simulate_default_is_low_hr(client):
    r = client.post("/api/simulate")
    assert r.status_code == 200
    assert r.json()["event_type"] == "LowHR"


def test_simulate_invalid_type_returns_400(client):
    r = client.post("/api/simulate?event_type=unknown")
    assert r.status_code == 400


def test_simulate_conflict_when_active(client):
    from agent.api import escalation
    escalation._handling = True
    try:
        r = client.post("/api/simulate?event_type=fall")
        assert r.status_code == 409
    finally:
        escalation._handling = False


def test_simulate_populates_recent_vitals(client):
    from agent.state import state
    client.post("/api/simulate?event_type=low_hr")
    assert len(state.recent_vitals) > 0


def test_wellbeing_after_simulate(client):
    client.post("/api/simulate?event_type=low_hr")
    r = client.post("/api/wellbeing")
    assert r.status_code == 200
