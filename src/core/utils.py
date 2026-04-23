from .settings import Settings, settings


def get_db_url(settings: Settings):
    return f'postgresql+asyncpg://{settings.db_user}:{settings.db_password}@{
        settings.db_address}:{settings.db_port}/{settings.db_name}'


def get_broker_url():
    return f"amqp://{settings.broker_user}:{
        settings.broker_password}@{settings.broker_url}:{settings.broker_port}"
