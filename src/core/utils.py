from .settings import Settings


def get_db_url(settings: Settings):
    return f'postgresql+asyncpg://{settings.db_user}:{settings.db_password}@{
        settings.db_address}:{settings.db_port}/{settings.db_name}'
