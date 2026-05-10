import time
from collections import deque

from agent.models import Vitals, AnomalyEvent, EventType
from agent.policy import EscalationPolicy


class Detector:
    """Aplica los 3 thresholds del MVP a cada lectura.
    Mantiene un buffer chico para detectar caída (spike + inmovilidad sostenida)."""

    def __init__(self, policy: EscalationPolicy):
        self.policy = policy
        self.recent_spikes: deque = deque(maxlen=10)  # (timestamp, peak_accel)
        self.last_alert_at = 0.0  # throttle: no más de 1 alerta cada 60s

    def evaluate(self, v: Vitals) -> AnomalyEvent | None:
        now = time.time()
        if (now - self.last_alert_at) < 60:
            return None

        accel_mag = (v.accel_x ** 2 + v.accel_y ** 2 + v.accel_z ** 2) ** 0.5

        if accel_mag > 3.0:
            self.recent_spikes.append((now, accel_mag))

        # Caída: hubo un spike en los últimos 30s y ahora está inmóvil
        recent = [(t, mag) for t, mag in self.recent_spikes if (now - t) < 30]
        if recent and not v.is_moving:
            self.last_alert_at = now
            spike_time = recent[0][0]   # primer spike registrado
            seconds_since_spike = now - spike_time
            return AnomalyEvent(
                type=EventType.FALL,
                severity=3,
                value=seconds_since_spike,   # segundos sin movimiento desde el impacto
                timestamp=v.timestamp,
            )

        # Bradicardia
        if v.heart_rate < self.policy.fc_threshold:
            self.last_alert_at = now
            return AnomalyEvent(
                type=EventType.LOW_HR,
                severity=2,
                value=v.heart_rate,
                timestamp=v.timestamp,
            )

        # Hipoxia
        if v.spo2 < self.policy.spo2_threshold:
            self.last_alert_at = now
            return AnomalyEvent(
                type=EventType.LOW_SPO2,
                severity=2,
                value=v.spo2,
                timestamp=v.timestamp,
            )

        return None
