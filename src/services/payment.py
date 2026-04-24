from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from broker.rabbit import broker
from db.db import get_async_session
from models import Payment
from shemas.payment import PaymentCreate, PaymentPublic


class PaymentService:
    def __init__(self,
                 session: AsyncSession = Depends(get_async_session)
                 ) -> None:
        self.session = session

    async def create_payment(self, paymentForm: PaymentCreate,
                             idempotency_key: str) -> PaymentPublic:
        payment = Payment(**paymentForm.model_dump(),
                          idempotency_key=idempotency_key)
        payment.webhook_url = str(payment.webhook_url)
        self.session.add(payment)
        await self.session.commit()
        await self.session.refresh(payment)
        await broker.publish(payment.id, queue="payment.new")
        return PaymentPublic(**payment.model_dump(
            include={"id", "status", "created_at"}))

    async def get_payment(self, id: int) -> Payment | None:
        payment = await self.session.execute(
            select(Payment).where(Payment.id == id))
        payment = payment.scalars().first()
        return payment
