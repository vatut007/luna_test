from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader
from http import HTTPStatus

from core.settings import settings


api_key_scheme = APIKeyHeader(name="X-API-Key")


async def verify_api_key(api_key: str = Depends(api_key_scheme)):
    if api_key != settings.api_key:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED,
                            detail="Invalid API Key")
    return api_key
