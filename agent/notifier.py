import os

from agent.models import AnomalyEvent


EVENT_LABELS = {
    "Fall": "Fall detected",
    "LowHR": "Low heart rate",
    "LowSpO2": "Low blood oxygen",
}


class Notifier:
    """Sends Telegram notifications. If no token is set, logs to stdout
    (useful for development and as a fallback if Telegram fails)."""

    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        self.contacts = [
            os.getenv("TELEGRAM_CHAT_ID_CONTACT_1", "").strip(),
            os.getenv("TELEGRAM_CHAT_ID_CONTACT_2", "").strip(),
        ]
        self.patient_name = os.getenv("PATIENT_NAME", "Carmen Garcia")

        if self.token:
            from telegram import Bot
            self.bot = Bot(token=self.token)
            print(f"[Notifier] Telegram enabled, contacts: {self.contacts}")
        else:
            self.bot = None
            print("[Notifier] No TELEGRAM_BOT_TOKEN — notifications to stdout")

    def _format_message(self, event: AnomalyEvent) -> str:
        label = EVENT_LABELS.get(event.type.value, event.type.value)
        return (
            "TE CUIDO ALERT\n\n"
            f"{self.patient_name} needs attention.\n\n"
            f"Event: {label}\n"
            f"Time: {event.timestamp}\n"
            f"Detail: value {event.value:.1f}\n\n"
            "Reply to this message to confirm you attended to them."
        )

    async def send(self, contact_idx: int, event: AnomalyEvent):
        chat_id = self.contacts[contact_idx] if contact_idx < len(self.contacts) else ""
        text = self._format_message(event)
        if self.bot and chat_id:
            try:
                await self.bot.send_message(chat_id=chat_id, text=text)
                print(f"[Notifier] Telegram sent to contact {contact_idx} (chat {chat_id})")
            except Exception as e:
                print(f"[Notifier] Error sending Telegram: {e}")
                print(f"[Notifier mock] {text}")
        else:
            print(f"[Notifier mock] would send to contact {contact_idx}:\n{text}\n")

    async def emergency(self, event: AnomalyEvent):
        # In production: Twilio Voice + private service
        print(f"[Notifier] *** ESCALATING TO EMERGENCY: {event.type.value} ***")
