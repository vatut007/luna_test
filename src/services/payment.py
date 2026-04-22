from typing import Annotated

from fastapi import Depends, Header

from db.db import get_async_session
from models import Payment
from shemas.payment import PaymentCreate, PaymentPublic

from sqlalchemy.ext.asyncio import AsyncSession


class PaymentService:
    def __init__(self,
                 payment: PaymentCreate,
                 idempotency_key: Annotated[str,
                                            Header(alias="Idempotency-Key")],
                 session: AsyncSession = Depends(get_async_session)
                 ) -> None:
        self.paymentForm = payment
        self.idempotency_key = idempotency_key
        self.session = session

    async def create_paymnet(self) -> PaymentPublic:
        payment = Payment(**self.paymentForm.model_dump(),
                          idempotency_key=self.idempotency_key)
        self.session.add(payment)
        await self.session.commit()
        await self.session.refresh(payment)
        return PaymentPublic(**payment.model_dump(
            include={"id", "status", "created_at"}))
