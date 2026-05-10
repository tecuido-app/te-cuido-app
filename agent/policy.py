from dataclasses import dataclass


@dataclass
class EscalationPolicy:
    fc_threshold: int = 40           # BPM mínimo (bradicardia)
    spo2_threshold: int = 90         # % mínimo (hipoxia)
    fall_immobile_secs: int = 600    # 10 min sin moverse después de spike
    grace_period_secs: int = 60      # ventana "estoy bien" en demo
    contact_timeout_secs: int = 180  # 3 min de espera por contacto


DEFAULT_POLICY = EscalationPolicy()
