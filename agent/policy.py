from dataclasses import dataclass


@dataclass
class EscalationPolicy:
    fc_threshold: int = 40           # minimum BPM (bradycardia)
    spo2_threshold: int = 90         # minimum % (hypoxia)
    fall_immobile_secs: int = 600    # 10 min immobile after impact spike
    grace_period_secs: int = 60      # wellbeing confirmation window
    contact_timeout_secs: int = 180  # 3 min wait per contact


DEFAULT_POLICY = EscalationPolicy()
