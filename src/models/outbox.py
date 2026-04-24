from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import JSON, TIMESTAMP, String
from sqlmodel import Column, Field, SQLModel


class OutboxStatus(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class OutboxMessage(SQLModel, table=True):
    idempotency_key: str | None = Field(default=None,
                                        primary_key=True,
                                        index=True)
    event_type: str = Field(
        sa_column=Column(String(200))
    )
    payload: dict = Field(
        sa_column=Column(JSON)
    )
    status: OutboxStatus = Field(default=OutboxStatus.PENDING)
    attempts: int = Field(default=0)
    next_attempt_at: datetime | None = Field(
        default=None,
        sa_column=Column(TIMESTAMP(timezone=True))
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(TIMESTAMP(timezone=True)))
    last_attempt_at: datetime | None = Field(
        default=None,
        sa_column=Column(TIMESTAMP(timezone=True))
    )
