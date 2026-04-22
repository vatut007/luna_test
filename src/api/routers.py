from fastapi import APIRouter
from .endpoints import payment_router


main_router = APIRouter(prefix='/api/v1')
main_router.include_router(payment_router)
