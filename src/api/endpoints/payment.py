from typing import Annotated
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.exc import IntegrityError

from services.payment import PaymentService
from shemas.payment import PaymentCreate, PaymentPublic
from models import Payment

router = APIRouter()


@router.post(
    "/payments",
    description="Создание платежа",
    name="Создание платежа",
    response_model=PaymentPublic,
    status_code=HTTPStatus.ACCEPTED
)
async def create_payment(
    payment: PaymentCreate,
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key")],
    paymentService: PaymentService = Depends()
):
    try:
        payment_public = await paymentService.create_payment(
            payment, idempotency_key)
    except IntegrityError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail=f"Платёж с idempotency_key={idempotency_key} уже существует"
        )
    return payment_public


@router.get(
    "/payments/{id}",
    description="Получение платежа",
    name="Получения платежа",
    response_model=Payment
)
async def get_router(id: int, paymentService: PaymentService = Depends()):
    payment = await paymentService.get_payment(id)
    if payment is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Не найден платеж с таким идентификатором"
        )
    return payment
