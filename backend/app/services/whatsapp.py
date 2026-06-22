"""WhatsApp service — sends messages via Twilio."""

import httpx
from app.core.config import settings


class WhatsAppClient:
    def __init__(self):
        self.account_sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.from_number = settings.TWILIO_WHATSAPP_NUMBER
        self.base_url = f"https://api.twilio.com/2010-04-01/Accounts/{self.account_sid}"

    async def send_message(self, to: str, body: str) -> dict:
        if not self.account_sid:
            return {"status": "skipped", "reason": "Twilio not configured"}

        url = f"{self.base_url}/Messages.json"
        data = {
            "From": f"whatsapp:{self.from_number}",
            "To": f"whatsapp:{to}",
            "Body": body,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url, data=data, auth=(self.account_sid, self.auth_token)
            )
            return response.json()


whatsapp_client = WhatsAppClient()
