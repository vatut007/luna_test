from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI

from api.routers import main_router
from core.settings import settings
from broker.rabbit import broker

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await broker.start()
    yield
    await broker.stop()

app = FastAPI(
    title=settings.project_name,
    docs_url='/api/v1/docs',
    openapi_url='/api/openapi.json',
    lifespan=lifespan
)

app.include_router(main_router)
