import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock

from agent.escalation import EscalationAgent
from agent.models import AnomalyEvent, EventType, ActionType
from agent.policy import EscalationPolicy
from agent.state import state


def make_event(event_type: EventType = EventType.LOW_HR) -> AnomalyEvent:
    return AnomalyEvent(
        type=event_type,
        severity=2,
        value=35.0,
        timestamp="2024-01-01T00:00:00+00:00",
    )


def mock_solana():
    s = MagicMock()
    s.register_event = AsyncMock(return_value=("pda_test", "tx_test"))
    s.register_action = AsyncMock(return_value="tx_action")
    s.confirm_wellbeing = AsyncMock(return_value="tx_confirm")
    return s


def mock_notifier():
    n = MagicMock()
    n.send = AsyncMock()
    n.emergency = AsyncMock()
    return n


def ai_dismisses():
    ai = MagicMock()
    ai.evaluate = AsyncMock(return_value={
        "real": False, "confidence": 0.9, "reasoning": "sensor noise"
    })
    return ai


def ai_confirms():
    ai = MagicMock()
    ai.evaluate = AsyncMock(return_value={
        "real": True, "confidence": 0.95, "reasoning": "genuine event"
    })
    return ai


def fast_policy(**kwargs) -> EscalationPolicy:
    defaults = dict(grace_period_secs=1, contact_timeout_secs=1)
    defaults.update(kwargs)
    return EscalationPolicy(**defaults)


@pytest.mark.asyncio
async def test_ai_dismissed_no_notification_no_state_change():
    agent = EscalationAgent(EscalationPolicy(), mock_notifier(), mock_solana(), ai_dismisses())
    n = mock_notifier()
    agent.notifier = n
    await agent.handle(make_event())
    n.send.assert_not_called()
    assert state.status == "ok"


@pytest.mark.asyncio
async def test_real_event_sets_alert_status():
    agent = EscalationAgent(fast_policy(), mock_notifier(), mock_solana(), ai_confirms())

    async def confirm_quickly():
        await asyncio.sleep(0.1)
        state.wellbeing_confirmed = True

    await asyncio.gather(agent.handle(make_event()), confirm_quickly())
    assert state.status == "ok"


@pytest.mark.asyncio
async def test_wellbeing_confirmed_during_grace_skips_notification():
    notifier = mock_notifier()
    agent = EscalationAgent(fast_policy(grace_period_secs=2), notifier, mock_solana(), ai_confirms())

    async def confirm():
        await asyncio.sleep(0.2)
        state.wellbeing_confirmed = True

    await asyncio.gather(agent.handle(make_event()), confirm())
    notifier.send.assert_not_called()
    assert state.status == "ok"


@pytest.mark.asyncio
async def test_contact_notified_after_grace_expires():
    notifier = mock_notifier()
    agent = EscalationAgent(fast_policy(), notifier, mock_solana(), ai_confirms())

    async def confirm_after_contact():
        await asyncio.sleep(1.5)
        state.wellbeing_confirmed = True

    await asyncio.gather(agent.handle(make_event()), confirm_after_contact())
    notifier.send.assert_called()


@pytest.mark.asyncio
async def test_concurrent_event_ignored_while_handling():
    notifier = mock_notifier()
    agent = EscalationAgent(fast_policy(grace_period_secs=2), notifier, mock_solana(), ai_confirms())

    async def confirm():
        await asyncio.sleep(0.2)
        state.wellbeing_confirmed = True

    # Second handle call should be a no-op because _handling is True
    await asyncio.gather(
        agent.handle(make_event()),
        agent.handle(make_event()),
        confirm(),
    )
    # AI was evaluated only once
    assert agent.ai.evaluate.call_count == 1


@pytest.mark.asyncio
async def test_solana_register_event_called():
    solana = mock_solana()
    agent = EscalationAgent(fast_policy(grace_period_secs=2), mock_notifier(), solana, ai_confirms())

    async def confirm():
        await asyncio.sleep(0.1)
        state.wellbeing_confirmed = True

    await asyncio.gather(agent.handle(make_event()), confirm())
    solana.register_event.assert_called_once()


@pytest.mark.asyncio
async def test_fall_event_handled():
    notifier = mock_notifier()
    agent = EscalationAgent(fast_policy(grace_period_secs=2), notifier, mock_solana(), ai_confirms())

    async def confirm():
        await asyncio.sleep(0.1)
        state.wellbeing_confirmed = True

    await asyncio.gather(agent.handle(make_event(EventType.FALL)), confirm())
    assert state.status == "ok"
