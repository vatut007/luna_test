from fastapi import FastAPI

from api.routers import main_router
from core.settings import settings

app = FastAPI(
    title=settings.project_name,
    docs_url='/api/v1/docs',
    openapi_url='/api/openapi.json'
)

app.include_router(main_router)
