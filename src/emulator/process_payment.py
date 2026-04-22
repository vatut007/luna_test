from faststream import FastStream
from faststream.rabbit import RabbitBroker, RabbitQueue
import httpx
from sqlmodel import select
from db.db import AsyncSessionLocal
from shemas.status import Status
import asyncio

from models.payment import Payment

broker = RabbitBroker("amqp://guest:guest@localhost:5672")
app = FastStream(broker)

payment_queue = RabbitQueue("payment.new", durable=True)


@broker.subscriber(payment_queue)
async def process_payment(payment_id: int):
    print(f"Обрабатываем платёж {payment_id}")

    await asyncio.sleep(2)  # задержка сети
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

    # Отправляем вебхук клиенту
    await send_webhook(payment)


async def send_webhook(payment: Payment):
    webhook_data = {
        "payment_id": payment.id,
        "status": payment.status.value,
        "amount": payment.amount,
        "currency": payment.currency,
        "customer_id": payment.customer_id
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