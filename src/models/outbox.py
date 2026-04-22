from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON, String
from datetime import datetime


class OutboxEvent(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    event_type: str = Field(
        max_length=100,
        description="Тип события (например, payment_created)"
    )
    payload: dict = Field(
        sa_column=Column(JSON),
        description="Данные события в формате JSON"
    )
    idempotency_key: str = Field(
        unique=True,
        index=True,
        max_length=64,
        description="Ключ идемпотентности для защиты от дублей"
    )
    status: str = Field(
        default="pending",
        sa_column=Column(String(20)),
        description="Статус: pending, published, failed"
    )
    attempt_count: int = Field(
        default=0,
        description="Количество попыток публикации"
    )
    last_attempt_at: datetime | None = Field(
        default=None,
        description="Время последней попытки публикации"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Дата создания события"
    )
    published_at: datetime | None = Field(
        default=None,
        description="Дата успешной публикации"
    )
