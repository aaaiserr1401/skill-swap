# SkillSwap

Учебный проект для обмена навыками между студентами.

## Запуск локально

1. Установить зависимости:

```
pip install -r requirements.txt
```

2. Применить миграции:

```
python manage.py migrate
```

3. Запустить сервер:

```
python manage.py runserver
```

## Запуск в Docker

```
docker compose up --build
```

Приложение будет доступно на http://localhost:8000.

## REST API (DRF)

- POST /api/auth/login/ — вход (получение токена)
- POST /api/auth/logout/ — выход (аннулирование токена)
- GET /api/users/ — список пользователей (+search)
- GET /api/users/{id}/ — профиль
- GET/POST /api/skills/ — навыки
- GET/PUT/DELETE /api/skills/{slug}/ — навык
- GET/POST /api/exchanges/ — заявки на обмен
- GET /api/exchanges/inbox/ — входящие заявки
- GET/PUT/DELETE /api/exchanges/{id}/ — заявка
- POST /api/exchanges/{id}/action/ — accept/decline/confirm

## Тесты

```
python manage.py test
```

## CI/CD

Готов workflow GitHub Actions в `.github/workflows/ci.yml` для автозапуска тестов при каждом пуше/PR.

## Нагрузочное тестирование

Файл `k6/script.js` — пример сценария для проверки основных эндпоинтов.
