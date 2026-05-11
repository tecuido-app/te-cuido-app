from dataclasses import dataclass, field
from typing import Literal, Optional
from collections import deque

from agent.models import EventLog, Vitals


Status = Literal["ok", "alert", "emergency"]


@dataclass
class AppState:
    status: Status = "ok"
    last_vitals: Optional[Vitals] = None
    active_event: Optional[EventLog] = None
    history: list = field(default_factory=list)
    recent_vitals: deque = field(default_factory=lambda: deque(maxlen=30))
    wellbeing_confirmed: bool = False


# shared singleton across subscriber, escalation, and api
state = AppState()
