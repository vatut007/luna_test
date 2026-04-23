from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=('.env',
                                                './env',
                                                '../.env',
                                                '../../.env'))
    project_name: str = "Асинхронный сервис процессинга платежей"
    db_name: str
    db_password: str
    db_user: str
    db_address: str
    db_port: str
    debug: bool = False
    broker_url: str
    broker_port: str
    broker_user: str
    broker_password: str


settings = Settings()
