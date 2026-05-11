from agent.detector import Detector
from agent.models import Vitals, EventType
from agent.policy import EscalationPolicy


def vitals(**kwargs) -> Vitals:
    base = dict(
        heart_rate=72.0, spo2=97.0, skin_temp=36.5,
        accel_x=0.0, accel_y=0.0, accel_z=1.0,
        gyro_x=0.0, gyro_y=0.0, gyro_z=0.0,
        is_moving=True, timestamp="2024-01-01T00:00:00+00:00",
    )
    base.update(kwargs)
    return Vitals(**base)


def fresh() -> Detector:
    return Detector(EscalationPolicy())


def test_normal_vitals_no_alert():
    assert fresh().evaluate(vitals()) is None


def test_bradycardia_below_threshold():
    d = fresh()
    result = d.evaluate(vitals(heart_rate=35.0))
    assert result is not None
    assert result.type == EventType.LOW_HR
    assert result.value == 35.0


def test_bradycardia_at_threshold_not_triggered():
    assert fresh().evaluate(vitals(heart_rate=40.0)) is None


def test_bradycardia_above_threshold_not_triggered():
    assert fresh().evaluate(vitals(heart_rate=60.0)) is None


def test_hypoxia_below_threshold():
    d = fresh()
    result = d.evaluate(vitals(spo2=85.0))
    assert result is not None
    assert result.type == EventType.LOW_SPO2
    assert result.value == 85.0


def test_hypoxia_at_threshold_not_triggered():
    assert fresh().evaluate(vitals(spo2=90.0)) is None


def test_alert_throttled_within_60s():
    d = fresh()
    first = d.evaluate(vitals(heart_rate=35.0))
    second = d.evaluate(vitals(heart_rate=35.0))
    assert first is not None
    assert second is None


def test_fall_spike_then_immobile():
    d = fresh()
    d.evaluate(vitals(accel_z=4.5, is_moving=True))  # impact spike
    result = d.evaluate(vitals(is_moving=False))       # immobile after spike
    assert result is not None
    assert result.type == EventType.FALL


def test_fall_immobile_without_prior_spike():
    assert fresh().evaluate(vitals(is_moving=False)) is None


def test_fall_spike_but_still_moving():
    d = fresh()
    d.evaluate(vitals(accel_z=4.5, is_moving=True))
    assert d.evaluate(vitals(is_moving=True)) is None


def test_bradycardia_takes_priority_over_normal():
    d = fresh()
    result = d.evaluate(vitals(heart_rate=30.0, spo2=85.0))
    # bradycardia check runs before hypoxia check
    assert result is not None
    assert result.type == EventType.LOW_HR
