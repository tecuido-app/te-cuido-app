import asyncio
import json
import os
import uuid

import gmqtt

from agent.models import Vitals
from agent.state import state
from agent.detector import Detector
from agent.escalation import EscalationAgent


BROKER = os.getenv("MQTT_BROKER", "broker.hivemq.com")
TOPIC_VITALS = os.getenv("MQTT_TOPIC_VITALS", "tecuido/carmen/vitals")


class Subscriber:
    def __init__(self, detector: Detector, agent: EscalationAgent):
        self.detector = detector
        self.agent = agent
        # unique client_id — public broker kicks duplicate IDs
        client_id = f"tecuido-agent-{uuid.uuid4().hex[:8]}"
        self.client = gmqtt.Client(client_id)
        print(f"[MQTT] client_id: {client_id}")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect

    def on_connect(self, client, flags, rc, properties):
        print(f"[MQTT] subscribed to {TOPIC_VITALS} on {BROKER}")
        self.client.subscribe(TOPIC_VITALS)

    def on_message(self, client, topic, payload, qos, properties):
        try:
            data = json.loads(payload.decode())
            vitals = Vitals.from_mqtt(data)
            state.last_vitals = vitals
            state.recent_vitals.append(vitals)

            event = self.detector.evaluate(vitals)
            if event and not state.active_event:
                # fire in background to avoid blocking the event loop
                asyncio.create_task(self.agent.handle(event))
        except Exception as e:
            print(f"[MQTT] error processing message: {e}")

    def on_disconnect(self, client, packet, exc=None):
        print("[MQTT] disconnected, reconnecting in 5s...")
        try:
            asyncio.get_running_loop().create_task(self.reconnect())
        except RuntimeError:
            pass  # no running loop (normal shutdown)

    async def reconnect(self):
        await asyncio.sleep(5)
        await self.client.connect(BROKER)

    async def run(self):
        await self.client.connect(BROKER)


async def subscribe_loop(detector: Detector, agent: EscalationAgent):
    """Infinite loop: connects to broker, listens for vitals, and on each
    reading runs the detector. If something is detected, fires the agent in background."""
    subscriber = Subscriber(detector, agent)
    await subscriber.run()
    # Keep running
    while True:
        await asyncio.sleep(1)
