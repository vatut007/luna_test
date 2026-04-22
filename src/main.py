from fastapi import FastAPI

from core.settings import settings
from api.routers import main_router


app = FastAPI(
    title=settings.project_name,
    docs_url='/api/v1/docs',
    openapi_url='/api/openapi.json'
)

app.include_router(main_router)
