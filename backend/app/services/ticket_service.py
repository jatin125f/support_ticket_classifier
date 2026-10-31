from datetime import datetime, timezone
from backend.app.db.session import SessionLocal
from backend.app.db.models import Ticket


def save_ticket(text: str, result: dict, db=None):
    """
    Persist a classified ticket to the database.
    """
    should_close = False
    if db is None:
        db = SessionLocal()
        should_close = True

    try:
        ticket = Ticket(
            text=text,
            category=result.get("category", "Unknown"),
            priority=result.get("priority", "Low"),
            confidence=float(result.get("confidence", 0.0)),
            method=result.get("method", "unknown"),
            suggested_reply=result.get("suggested_reply", ""),
            status=result.get("status", "Open"),
            created_at=datetime.now(timezone.utc)
        )

        db.add(ticket)
        db.commit()
        db.refresh(ticket)
        return ticket

    finally:
        if should_close:
            db.close()


if __name__ == "__main__":
    test_result = {
        "category": "Payment",
        "priority": "High",
        "confidence": 0.67,
        "method": "rules + ml",
        "suggested_reply": "We understand that there is an issue with your payment."
    }

    ticket = save_ticket(
        "My payment was deducted but my order is pending",
        test_result
    )

    print("\n===== DATABASE TEST =====")
    print("Ticket saved successfully!")
    print("Ticket ID:", ticket.id)
    print("Category:", ticket.category)
    print("Priority:", ticket.priority)
    print("Status:", ticket.status)