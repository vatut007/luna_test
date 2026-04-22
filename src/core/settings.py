from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    project_name: str = "Асинхронный сервис процессинга платежей"
    db_name: str
    db_password: str
    db_user: str
    db_address: str
    db_port: str
    debug: bool = False


settings = Settings()
