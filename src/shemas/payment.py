from datetime import datetime

from pydantic import BaseModel, Field, HttpUrl

from .currency import Currency
from .status import Status


class PaymentCreate(BaseModel):
    amount: float = Field(
        description="Сумма платежа",
    )
    currency: Currency = Field(
        description="Валюта: RUB, USD, EUR",
    )
    description: str | None = Field()
    metadata: dict | None = Field()
    webhook_url: HttpUrl = Field()


class PaymentPublic(BaseModel):
    id: int
    status: Status = Field(
        default=Status.PENDING,
        description="Статус платежа: pending, succeeded, failed"
    )
    created_at: datetime = Field(
        description="Дата и время создания платежа"
    )


class PaymentWebhook(BaseModel):
    payment_id: int | None
    status: str
    amount: float
    currency: str
