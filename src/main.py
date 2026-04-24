import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI

from api.routers import main_router
from broker.rabbit import broker
from core.settings import settings
from depends.auth import verify_api_key

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await broker.start()
    yield
    await broker.stop()

app = FastAPI(
    dependencies=[Depends(verify_api_key)],
    title=settings.project_name,
    docs_url='/api/v1/docs',
    openapi_url='/api/openapi.json',
    lifespan=lifespan
)

app.include_router(main_router)
