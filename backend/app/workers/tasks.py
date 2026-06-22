"""Celery background tasks."""

from datetime import datetime, timedelta
from app.workers.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.credit import Credit
from app.models.debtor import Debtor
from app.models.reminder_log import ReminderLog


@celery_app.task(name="app.workers.tasks.mark_overdue", bind=True)
def mark_overdue(self):
    """Mark credits as overdue if past due date."""
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        overdue_credits = db.query(Credit).filter(
            Credit.status == "active",
            Credit.is_active == True,
            Credit.due_date < now,
        ).all()

        count = 0
        for credit in overdue_credits:
            credit.status = "overdue"
            count += 1

        db.commit()
        return {"marked_overdue": count}
    except Exception as e:
        db.rollback()
        raise self.retry(exc=e, countdown=60)
    finally:
        db.close()


@celery_app.task(name="app.workers.tasks.send_reminders", bind=True)
def send_reminders(self):
    """Send payment reminders for overdue credits."""
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        reminder_threshold = now - timedelta(hours=24)

        # Find overdue credits that haven't been reminded in 24h
        credits = db.query(Credit, Debtor).join(Debtor).filter(
            Credit.status == "overdue",
            Credit.is_active == True,
            ~Credit.reminder_logs.any(
                ReminderLog.sent_at > reminder_threshold
            ),
        ).all()

        sent = 0
        for credit, debtor in debtor_credits:
            if debtor.phone:
                # In production, call whatsapp_client.send_message here
                log = ReminderLog(
                    credit_id=credit.id,
                    channel="whatsapp",
                    status="sent",
                    message=f"Reminder sent to {debtor.name}",
                )
                db.add(log)
                sent += 1

        db.commit()
        return {"reminders_sent": sent}
    except Exception as e:
        db.rollback()
        raise self.retry(exc=e, countdown=60)
    finally:
        db.close()
