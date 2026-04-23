from fastapi import APIRouter, Depends

from services.payment import PaymentService
from shemas.payment import PaymentPublic

router = APIRouter()


@router.post(
    "/payments",
    description="Создание платежа",
    name="Создание платежа",
    response_model=PaymentPublic
)
async def create_payment(
    paymentService: PaymentService = Depends()
):
    payment_public = await paymentService.create_paymnet()
    return payment_public
