from typing import Annotated
from fastapi import APIRouter, Header
from fastapi.responses import JSONResponse
from services.payment import PaymentService
from shemas.payment import PaymentCreate, PaymentPublic


router = APIRouter()


@router.post(
        "/payments",
        description="Создание платежа",
        name="Создание платежа",
        response_model=PaymentPublic
)
async def create_payment(
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key")],
    payment: PaymentCreate,
):
    return JSONResponse('Привет')
