import os

from agent.models import AnomalyEvent


EVENT_LABELS = {
    "Fall": "Caída detectada",
    "LowHR": "Frecuencia cardíaca baja",
    "LowSpO2": "Oxígeno en sangre bajo",
}


class Notifier:
    """Envía notificaciones por Telegram. Si no hay token, loguea a stdout
    (útil para desarrollo y como fallback en demo si falla Telegram)."""

    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
        self.contacts = [
            os.getenv("TELEGRAM_CHAT_ID_CONTACT_1", "").strip(),
            os.getenv("TELEGRAM_CHAT_ID_CONTACT_2", "").strip(),
        ]
        self.patient_name = os.getenv("PATIENT_NAME", "Carmen García")

        if self.token:
            from telegram import Bot
            self.bot = Bot(token=self.token)
            print(f"[Notifier] Telegram habilitado, contactos: {self.contacts}")
        else:
            self.bot = None
            print("[Notifier] Sin TELEGRAM_BOT_TOKEN — notificaciones a stdout")

    def _format_message(self, event: AnomalyEvent) -> str:
        label = EVENT_LABELS.get(event.type.value, event.type.value)
        return (
            "ALERTA TE CUIDO\n\n"
            f"{self.patient_name} necesita atencion.\n\n"
            f"Evento: {label}\n"
            f"Hora: {event.timestamp}\n"
            f"Detalle: valor {event.value:.1f}\n\n"
            "Respondé este mensaje para confirmar que la atendiste."
        )

    async def send(self, contact_idx: int, event: AnomalyEvent):
        chat_id = self.contacts[contact_idx] if contact_idx < len(self.contacts) else ""
        text = self._format_message(event)
        if self.bot and chat_id:
            try:
                await self.bot.send_message(chat_id=chat_id, text=text)
                print(f"[Notifier] Telegram enviado a contacto {contact_idx} (chat {chat_id})")
            except Exception as e:
                print(f"[Notifier] Error enviando Telegram: {e}")
                print(f"[Notifier mock] {text}")
        else:
            print(f"[Notifier mock] would send to contact {contact_idx}:\n{text}\n")

    async def emergency(self, event: AnomalyEvent):
        # En producción: Twilio Voice + servicio privado tipo Vittal
        print(f"[Notifier] *** ESCALANDO A EMERGENCIA: {event.type.value} ***")
