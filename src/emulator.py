import asyncio
from datetime import datetime, timedelta, timezone

import httpx
from faststream import FastStream, Logger
from faststream.rabbit import RabbitQueue
from sqlmodel import select

from broker.rabbit import broker
from db.db import AsyncSessionLocal
from models.outbox import OutboxMessage, OutboxStatus
from models.payment import Payment
from shemas.payment import PaymentWebhook, WebhookPayload
from shemas.status import Status

payment_queue = RabbitQueue("payment.new", durable=True)
dlq_queue_payment = RabbitQueue("dlq.payment", durable=True)
dlq_queue_webhooks = RabbitQueue("dlq.webhooks", durable=True)
webhook_queue = RabbitQueue("webhook.events",
                            durable=False,
                            arguments={
                                "x-dead-letter-exchange": "",
                                "x-dead-letter-routing-key": "dlq.webhooks"
                            })
app = FastStream(broker)
OUTBOX_POLL_INTERVAL = 10
MAX_RETRIES = 3
BACKOFF_FACTOR = 2


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
        outbox_message = OutboxMessage(
            idempotency_key=payment.idempotency_key,
            event_type="payment_status_updated",
            payload=WebhookPayload(
                payment_id=payment.id,
                status=payment.status,
                amount=payment.amount,
                currency=payment.currency,
                webhook_url=payment.webhook_url,
                idempotency_key=payment.idempotency_key
            ).model_dump(),
            next_attempt_at=datetime.now(timezone.utc),
        )
        session.add(outbox_message)
        await session.commit()
        await session.refresh(outbox_message)

    logger.info(f"Платёж {payment_id} обработан, событие добавлено в Outbox")
    await broker.publish(outbox_message.payload, webhook_queue)


@broker.subscriber(webhook_queue)
async def send_webhook(payload: WebhookPayload, logger: Logger):
    async with AsyncSessionLocal() as session:
        query = await session.execute(
            select(OutboxMessage).where(
                OutboxMessage.idempotency_key == payload.idempotency_key)
            .with_for_update())
        outbox_message = query.scalars().first()
        if outbox_message is None:
            logger.error("OutboxMessage is None")
            return
        try:
            payment_webhook = PaymentWebhook(
                **payload.model_dump(
                    exclude={"webhook_url"}))
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    payload.webhook_url,
                    json=payment_webhook.model_dump(),
                    timeout=10.0
                )
                response.raise_for_status()
                outbox_message.sqlmodel_update({
                    "status": OutboxStatus.SENT,
                    "last_attempt_at": datetime.now(timezone.utc),
                    "next_attempt_at": None,
                    "attempts": outbox_message.attempts + 1
                })
                session.add(outbox_message)
                await session.commit()
            logger.info(f"Вебхук отправлен, статус: {response.status_code}")
        except Exception as e:
            delay = timedelta(seconds=30 * (
                BACKOFF_FACTOR**(outbox_message.attempts - 1)))
            next_attempt_at = datetime.now(timezone.utc) + delay
            outbox_message.sqlmodel_update({
                "status": OutboxStatus.FAILED,
                "next_attempt_at": next_attempt_at,
                "attempts": outbox_message.attempts + 1,
                "last_attempt_at": datetime.now(timezone.utc)
            })
            session.add(outbox_message)
            await session.commit()
            await session.refresh(outbox_message)
            logger.error(f"Ошибка отправки вебхука: {e}")


async def outbox_relay():
    while True:
        async with AsyncSessionLocal() as session:
            now = datetime.now(timezone.utc)
            query = select(OutboxMessage).where(
                (OutboxMessage.status == OutboxStatus.FAILED) &
                (OutboxMessage.next_attempt_at <= now) &
                (OutboxMessage.attempts < MAX_RETRIES)
            ).limit(10)

            result = await session.execute(query)
            messages = result.scalars().all()
            for message in messages:
                await broker.publish(
                    message.payload, queue=webhook_queue)
                message.status = OutboxStatus.PENDING
                session.add(message)
                await session.commit()
                await session.refresh(message)
        await asyncio.sleep(OUTBOX_POLL_INTERVAL)


@app.on_startup
async def start_outbox_relay():
    asyncio.create_task(outbox_relay())
