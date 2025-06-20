# Bank Webhooks Service

Django сервис для обработки банковских webhook-уведомлений и управления балансом организаций.

## 🚀 Запуск проекта

1. Убедитесь, что у вас установлены Docker и Docker Compose
2. Клонируйте репозиторий
3. Выполните команды:


docker-compose build
docker-compose up

### Сервис будет доступен по адресу: http://localhost:8000

## 📚 API Endpoints
1. Обработка webhook-уведомления
POST /api/webhook/bank/

###  Пример запроса:

json
{
  "operation_id": "ccf0a86d-041b-4991-bcf7-e2352f7b8a4a",
  "amount": 145000,
  "payer_inn": "1234567890",
  "document_number": "PAY-328",
  "document_date": "2024-04-27T21:00:00Z"
}
Ответ:

200 OK - успешная обработка или дубликат

400 Bad Request - невалидные данные

### Получение баланса организации

GET /api/organizations/<inn>/balance/

### Пример ответа:

json
{
  "inn": "1234567890",
  "balance": 145000
}
## 🧪 Тестирование
Для запуска тестов выполните:

docker-compose run web python manage.py test api
## 🛠 Технологии
Python 3.9

Django 4.2.17

Django REST Framework

MySQL

Docker

## 🔒 Защита от дублей
Сервис проверяет уникальность operation_id и не обрабатывает повторные webhook-и с тем же ID операции.

text

## Как использовать

###  Собрать и запустить контейнеры:

docker-compose up -d
Создать и применить миграции:


docker-compose exec web python manage.py migrate
### Отправить тестовый webhook:


curl -X POST http://localhost:8000/api/webhook/bank/ \
  -H "Content-Type: application/json" \
  -d '{
    "operation_id": "ccf0a86d-041b-4991-bcf7-e2352f7b8a4a",
    "amount": 145000,
    "payer_inn": "1234567890",
    "document_number": "PAY-328",
    "document_date": "2024-04-27T21:00:00Z"
  }'

### Проверить баланс:

curl http://localhost:8000/api/organizations/1234567890/balance/
