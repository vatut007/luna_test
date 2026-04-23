import asyncio

from faststream import FastStream, Logger
import httpx
from faststream.rabbit import RabbitQueue
from sqlmodel import select

from db.db import AsyncSessionLocal
from models.payment import Payment
from shemas.status import Status
from shemas.payment import PaymentWebhook
from broker.rabbit import broker

payment_queue = RabbitQueue("payment.new", durable=True)

app = FastStream(broker)


@broker.subscriber(payment_queue)
async def process_payment(payment_id: int, logger: Logger):
    logger.info(f"Обрабатываем платёж {payment_id}")
    await asyncio.sleep(2)
    success = True
    async with AsyncSessionLocal() as session:
        payment = await session.execute(
            select(Payment).where(Payment.id == payment_id))
        payment = payment.scalars().first()
        if payment is None:
            logger.info("Payment не найден")
            return
        if success:
            payment.status = Status.SUCCEEDED
        else:
            payment.status = Status.FAILED
        session.add(payment)
        await session.commit()
        await session.refresh(payment)
    await send_webhook(payment, logger)


async def send_webhook(payment: Payment, logger: Logger):
    payment_webhook = PaymentWebhook(
        payment_id=payment.id,
        status=payment.status,
        amount=payment.amount,
        currency=payment.currency
    )

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                payment.webhook_url,
                json=payment_webhook.model_dump(),
                timeout=10.0
            )
            logger.info(f"Вебхук отправлен, статус: {response.status_code}")
        except Exception as e:
            logger.error(f"Ошибка отправки вебхука: {e}")
