# luna_test
[Задание] (https://disk.360.yandex.ru/d/IotgLh3PV_XbaQ)

## Как запустить приложение?
1) Создать .env в app/.env со следующими переменными

```env
DB_NAME=db_example
DB_PASSWORD=user_example
DB_USER=password_example
DB_ADDRESS=localhost
DB_PORT=5432
BROKER_URL=localhost
BROKER_PORT=5672
BROKER_USER=user_example
BROKER_PASSWORD=password_example
API_KEY=key_example
```
Выполнить 

```bash
docker-compose up -d 
```

Сервис будет доступен по http://localhost:8000/api/v1  
Документация http://localhost:8000/api/v1/docs

Можно выполнить Post-запрос по api/v1/payments. В header указать ключ X-API-Key из файла .env переменая API_KEY

```json
{
    "amount": 500,
    "currency": "EUR",
    "description": "Оплата по договору №6500",
    "metadata": {"organization":"ООО 'Ветер'"},
    "webhook_url": "veter.ru/api/v1/create_payment"
}
```

Будет выполнен запрос на создание платежа. Он появится в таблице payment в состоянии pending. Затем отправится сообщение в очередь payment.new
Отдельный сервис Consumer(файл emulator.py) получит это сообщение, обработает его, и изменит статус платежа в БД в таблице payment.
После этого будет выполнен запрос по webhook. Будет создана запись в таблице outboxmessage со статусо pending. А также отправлено сообщение в очередь webhook.events
Функция send_webhook из файла emulator.py читает сообщения из очереди webhook.events и выполняет запрос. Если запрос был неудачным, то увеличивается количество attempts, меняется статус на failed.
Далее функция outbox_relay переодически проверяет какие webhooks не удалось отправить, по условию, что дата следующей попытки меньше даты которая сейчас, статус outboxMessage Failed, и количество попыток не больше 3. Затем публикует эти данные в webhook.events

Если выполнить 
```json

{
  "order_id": 1,
  "product_id": 1,
  "quantity": 100
}
```