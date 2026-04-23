import asyncio

import httpx
from faststream import FastStream
from faststream.rabbit import RabbitBroker, RabbitQueue
from sqlmodel import select

from core.utils import get_broker_url
from db.db import AsyncSessionLocal
from models.payment import Payment
from shemas.status import Status

broker = RabbitBroker(get_broker_url())
app = FastStream(broker)

payment_queue = RabbitQueue("payment.new", durable=True)


@broker.subscriber(payment_queue)
async def process_payment(payment_id: int):
    print(f"Обрабатываем платёж {payment_id}")
    await asyncio.sleep(2)
    success = True
    async with AsyncSessionLocal() as session:
        payment = await session.execute(
            select(Payment).where(Payment.id == payment_id))
        payment = payment.scalars().first()
        if payment is None:
            print("Payment не найден")
            return
        if success:
            payment.status = Status.SUCCEEDED
        else:
            payment.status = Status.FAILED
        session.add(payment)
        await session.commit()
    await send_webhook(payment)


async def send_webhook(payment: Payment):
    webhook_data = {
        "payment_id": payment.id,
        "status": payment.status,
        "amount": payment.amount,
        "currency": payment.currency
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                payment.webhook_url,
                json=webhook_data,
                timeout=10.0
            )
            print(f"Вебхук отправлен, статус: {response.status_code}")
        except Exception as e:
            print(f"Ошибка отправки вебхука: {e}")
