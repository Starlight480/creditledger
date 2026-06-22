"""Notification dispatcher — sends reminders via WhatsApp."""

from app.services.whatsapp import whatsapp_client


async def send_payment_reminder(phone: str, debtor_name: str, amount: float, due_date: str = None):
    message = f"Hi {debtor_name}, this is a friendly reminder that you have an outstanding balance of ₦{amount:,.2f}."
    if due_date:
        message += f" Please pay by {due_date}."
    message += " Thank you!"

    return await whatsapp_client.send_message(phone, message)
