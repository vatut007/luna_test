from .currency import Currency
from .status import Status
from pydantic import BaseModel, Field
from datetime import datetime


class PaymentCreate(BaseModel):
    amount: float = Field(
        description="Сумма платежа",
    )
    currency: Currency = Field(
        description="Валюта: RUB, USD, EUR",
    )
    description: str | None
    metadata: dict | None
    webhook_url: str


class PaymentPublic(BaseModel):
    id: int
    status: Status = Field(
        default=Status.PENDING,
        description="Статус платежа: pending, succeeded, failed"
    )
    created_at: datetime = Field(
        description="Дата и время создания платежа"
    )
