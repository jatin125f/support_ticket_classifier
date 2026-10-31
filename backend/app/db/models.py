from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from backend.app.db.session import Base


def get_utc_now():
    return datetime.now(timezone.utc)


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)

    text = Column(Text, nullable=False)

    category = Column(String, nullable=False)

    priority = Column(String, nullable=False)

    confidence = Column(Float, nullable=False)

    method = Column(String, nullable=False)

    suggested_reply = Column(Text, nullable=True)

    status = Column(
        String,
        default="Open",
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=get_utc_now,
        nullable=True
    )