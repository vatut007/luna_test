#!/bin/sh
set -e

echo "Ожидание готовности БД..."


# Python‑проверка подключения к БД
while true; do
    python -c "
import os
from sqlalchemy import create_engine
try:
    engine = create_engine(
        f'postgresql+psycopg2://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@'
        f'{os.getenv('DB_ADDRESS')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}'
    )
    engine.connect()
    print('БД готова!')
    exit(0)
except Exception as e:
    print(f'Ошибка подключения: {e}')
    exit(1)
" && break  # Если подключение успешно — выходим из цикла

    echo "БД ещё не готова — жду 2 секунды..."
    sleep 2
done

echo "Запуск миграций Alembic..."
alembic upgrade head


echo "Миграции завершены. Запуск приложения..."
cd src
exec "$@"