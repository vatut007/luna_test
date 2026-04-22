from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (AsyncSession, create_async_engine,
                                    async_sessionmaker)
from core.settings import settings
from core.utils import get_db_url

url = get_db_url(settings)
engine = create_async_engine(url)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession)


async def get_async_session():
    async with AsyncSessionLocal() as async_session:
        yield async_session
