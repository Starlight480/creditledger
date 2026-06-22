"""Webhook routes — Twilio WhatsApp, Paystack."""

from fastapi import APIRouter, Request, HTTPException

router = APIRouter()


@router.post("/twilio")
async def twilio_webhook(request: Request):
    """Handle incoming WhatsApp messages from Twilio."""
    form = await request.form()
    from_number = form.get("From", "")
    body = form.get("Body", "").strip().lower()

    # Simple auto-reply for now
    # In production, parse commands, link to debtor/credit, etc.
    return {
        "status": "received",
        "from": from_number,
        "message": body,
    }


@router.post("/paystack")
async def paystack_webhook(request: Request):
    """Handle Paystack payment events."""
    payload = await request.json()
    event = payload.get("event")

    if event == "charge.success":
        # Process successful payment
        data = payload.get("data", {})
        reference = data.get("reference")
        amount = data.get("amount", 0) / 100  # Paystack sends in kobo
        # TODO: Match reference to credit and record payment
        return {"status": "processed", "reference": reference, "amount": amount}

    return {"status": "ignored", "event": event}
