from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON, String, Numeric
from datetime import datetime


class Payment(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    amount: float = Field(
        sa_column=Column(Numeric(10, 2)),
        description="Сумма платежа"
    )
    currency: str = Field(
        max_length=3,
        sa_column=Column(String(3)),
        description="Валюта: RUB, USD, EUR"
    )
    description: str | None = Field(
        default=None,
        max_length=255,
        description="Описание платежа"
    )
    metadata_: dict | None = Field(
        default=None,
        sa_column=Column(JSON),
        description="Дополнительные метаданные в формате JSON"
    )
    status: str = Field(
        default="pending",
        sa_column=Column(String(20)),
        description="Статус платежа: pending, succeeded, failed"
    )
    idempotency_key: str = Field(
        unique=True,
        index=True,
        max_length=64,
        description="Уникальный ключ для защиты от дублирования"
    )
    webhook_url: str | None = Field(
        default=None,
        max_length=512,
        description="URL для вебхука (уведомления о результате)"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Дата и время создания платежа"
    )
    processed_at: datetime | None = Field(
        default=None,
        description="Дата и время обработки платежа"
    )
