import json
import os

import google.genai as genai
from google.genai import types

from agent.models import Vitals, AnomalyEvent


GEMINI_MODEL = "gemini-2.5-flash"


class AIFilter:
    """Passes the candidate event + recent readings to Gemini.
    Returns {real, confidence, reasoning}.
    If no API key is configured, it is disabled and always returns real=true."""

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("[AIFilter] GEMINI_API_KEY or GOOGLE_API_KEY not set — filter disabled")
            self.client = None
        else:
            self.client = genai.Client(api_key=api_key)

    async def evaluate(self, event: AnomalyEvent, recent_vitals: list[Vitals]) -> dict:
        if self.client is None:
            return {
                "real": True,
                "confidence": 1.0,
                "reasoning": "AI filter disabled (no API key)",
            }

        readings = "\n".join(
            f"- HR={v.heart_rate:.0f}bpm SpO2={v.spo2:.1f}% "
            f"accel=({v.accel_x:.2f},{v.accel_y:.2f},{v.accel_z:.2f})g "
            f"moving={v.is_moving}"
            for v in recent_vitals[-15:]
        )

        prompt = f"""You are a medical assistant evaluating an alert from an elderly monitoring system.

PATIENT: Carmen Garcia, 78 years old, lives alone.

DETECTED EVENT:
- Type: {event.type.value}
- Value: {event.value:.1f}
- Severity: {event.severity}/3

RECENT READINGS (most recent last):
{readings}

Is this a real emergency or likely a false positive (sudden movement, sensor misplacement, sitting down quickly)?

Respond with ONLY a JSON object in this exact format, no additional text:
{{"real": true|false, "confidence": 0.0-1.0, "reasoning": "one short sentence"}}"""

        try:
            response = await self.client.aio.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                ),
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"[AIFilter] evaluation error, falling back to real=true: {e}")
            return {
                "real": True,
                "confidence": 0.5,
                "reasoning": f"Fallback (AI error: {type(e).__name__})",
            }
