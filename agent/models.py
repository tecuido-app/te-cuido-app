from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class EventType(str, Enum):
    FALL = "Fall"
    LOW_HR = "LowHR"
    LOW_SPO2 = "LowSpO2"


class ActionType(str, Enum):
    GRACE_PERIOD = "GracePeriod"
    AI_DISMISSED = "AIDismissed"
    NOTIFIED_CONTACT = "NotifiedContact"
    ESCALATED = "Escalated"
    WELLBEING_CONFIRMED = "WellbeingConfirmed"
    RESOLVED = "Resolved"


@dataclass
class Vitals:
    heart_rate: float
    spo2: float
    skin_temp: float
    accel_x: float
    accel_y: float
    accel_z: float
    gyro_x: float
    gyro_y: float
    gyro_z: float
    is_moving: bool
    timestamp: str

    @classmethod
    def from_mqtt(cls, payload: dict) -> "Vitals":
        return cls(
            heart_rate=payload["heart_rate"],
            spo2=payload["spo2"],
            skin_temp=payload["skin_temp"],
            accel_x=payload["accel"]["x"],
            accel_y=payload["accel"]["y"],
            accel_z=payload["accel"]["z"],
            gyro_x=payload["gyro"]["x"],
            gyro_y=payload["gyro"]["y"],
            gyro_z=payload["gyro"]["z"],
            is_moving=payload["is_moving"],
            timestamp=payload["timestamp"],
        )


@dataclass
class AnomalyEvent:
    type: EventType
    severity: int
    value: float
    timestamp: str


@dataclass
class AgentAction:
    type: ActionType
    timestamp: str
    tx_hash: str = ""
    contact_index: Optional[int] = None
    note: Optional[str] = None


@dataclass
class EventLog:
    id: str
    type: EventType
    severity: int
    value: float
    timestamp: str
    actions: list = field(default_factory=list)
    resolved: bool = False
    resolved_at: Optional[str] = None
    event_started_at: Optional[str] = None
