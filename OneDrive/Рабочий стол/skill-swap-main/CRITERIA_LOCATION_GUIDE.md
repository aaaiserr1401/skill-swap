# Руководство по расположению компонентов по критериям

Этот документ показывает, где именно в проекте находится реализация каждого критерия.

---

## 1. АУТЕНТИФИКАЦИЯ ПОЛЬЗОВАТЕЛЕЙ (регистрация, вход, выход)

### Регистрация
- **Файл:** `accounts/views.py`
  - Функция: `register()` (строки 23-33)
- **Файл:** `accounts/forms.py`
  - Класс: `RegisterForm` (строки 6-25)
- **URL:** `accounts/urls.py` → `path('register/', register, name='register')` (строка 19)
- **Шаблон:** `templates/accounts/register.html`

### Вход
- **Файл:** `accounts/views.py`
  - Класс: `UserLoginView` (строки 14-16)
- **Файл:** `accounts/forms.py`
  - Класс: `LoginForm` (строки 28-30)
- **URL:** `accounts/urls.py` → `path('login/', UserLoginView.as_view(), name='login')` (строка 17)
- **Шаблон:** `templates/accounts/login.html`

### Выход
- **Файл:** `accounts/views.py`
  - Класс: `UserLogoutView` (строки 19-20)
- **URL:** `accounts/urls.py` → `path('logout/', UserLogoutView.as_view(), name='logout')` (строка 18)
- **Шаблон:** `templates/accounts/logout.html`

### Модель пользователя
- **Файл:** `accounts/models.py`
  - Класс: `User(AbstractUser)` (строки 31-64)
  - Расширяет Django AbstractUser с дополнительными полями

---

## 2. РОЛИ ПОЛЬЗОВАТЕЛЕЙ (обычный пользователь и администратор)

### Модель ролей
- **Файл:** `accounts/models.py`
  - Поле: `role` (строка 47)
  - Константы: `ROLE_USER`, `ROLE_ADMIN`, `ROLE_MODERATOR` (строки 32-34)
  - Методы: `is_admin_user()`, `is_moderator()`, `can_manage_content()` (строки 56-64)
- **Миграция:** `accounts/migrations/0009_user_role.py`

### Разрешения
- **Файл:** `accounts/permissions.py`
  - Классы: `IsAdminOrReadOnly`, `IsModeratorOrReadOnly`, `IsOwnerOrModerator`

### Проверка доступа к админ-панели
- **Файл:** `accounts/admin_views.py`
  - Функция: `is_admin(user)` (строки 14-16)
  - Используется декоратор `@user_passes_test(is_admin)`

### Админ-панель Django
- **Файл:** `accounts/admin.py`
  - Класс: `UserAdmin` (строки 6-35)
  - Поле `role` добавлено в fieldsets и list_display

---

## 3. ОСНОВНАЯ ФУНКЦИОНАЛЬНОСТЬ ВЫБРАННОЙ ТЕМЫ

### Модели данных
- **Файл:** `accounts/models.py`
  - `Skill` (строки 6-28) - навыки
  - `User` (строки 31-64) - пользователи с навыками
  - `ExchangeRequest` (строки 46-146) - запросы на обмен

### Управление навыками
- **Файл:** `core/views.py`
  - `skill_list()` (строки 13-28) - список навыков
  - `skill_detail()` (строки 31-40) - детали навыка
  - `skill_add()` (строки 43-70) - добавление навыка
- **URL:** `core/urls.py`

### Профили пользователей
- **Файл:** `accounts/views.py`
  - `profile_detail()` (строки 50-59) - просмотр профиля
  - `profile_edit()` (строки 36-47) - редактирование профиля
- **Файл:** `accounts/forms.py`
  - Класс: `ProfileForm` (строки 33-51)

### Система обмена навыками
- **Файл:** `accounts/views.py`
  - `exchange_create()` (строки 69-85) - создание обмена
  - `exchange_accept()` (строки 136-151) - принятие обмена
  - `exchange_decline()` (строки 155-169) - отклонение обмена
  - `exchange_confirm()` (строки 180-211) - подтверждение завершения
  - `exchange_list()` (строки 63-65) - список обменов
  - `exchange_detail()` (строки 215-217) - детали обмена

### Система баллов
- **Файл:** `accounts/models.py`
  - Поля: `points`, `points_hold` (строки 45-46)
  - Методы в `ExchangeRequest`:
    - `hold_from_sender()` (строки 77-101) - блокировка баллов
    - `refund_to_sender()` (строки 103-119) - возврат баллов
    - `try_complete()` (строки 121-146) - завершение обмена с переводом баллов

---

## 4. АДМИН-ПАНЕЛЬ ДЛЯ УПРАВЛЕНИЯ КОНТЕНТОМ

### Админ-панель приложения
- **Файл:** `accounts/admin_views.py`
  - `admin_dashboard()` (строки 20-65) - главная страница с статистикой
  - `admin_users()` (строки 69-85) - управление пользователями
  - `admin_user_detail()` (строки 89-100) - детали пользователя
  - `admin_skills()` (строки 104-120) - управление навыками
  - `admin_exchanges()` (строки 124-140) - управление обменами
  - `admin_exchange_detail()` (строки 144-151) - детали обмена
- **URL:** `accounts/urls.py` (строки 34-39)
  - `/accounts/admin-panel/` - дашборд
  - `/accounts/admin-panel/users/` - пользователи
  - `/accounts/admin-panel/skills/` - навыки
  - `/accounts/admin-panel/exchanges/` - обмены
- **Шаблоны:** `templates/admin/`
  - `dashboard.html` - дашборд
  - `users.html` - список пользователей

### Django Admin (стандартная админка)
- **Файл:** `accounts/admin.py`
  - `UserAdmin` (строки 6-35)
  - `SkillAdmin` (строки 38-41)
  - `ExchangeRequestAdmin` (строки 44-48)
- **URL:** `/admin/` (настроен в `skillswap/urls.py`)

---

## 5. АДАПТИВНЫЙ ИНТЕРФЕЙС (десктоп + мобильная версия)

### CSS стили
- **Файл:** `static/css/style.css`
  - Медиа-запросы для мобильных:
    - `@media (max-width: 640px)` (строки 33-36, 95, 147-149, 176-187)
    - `@media (min-width: 768px)` (строки 93, 99)
    - `@media (min-width: 900px)` (строка 135)
  - Адаптивная сетка: `grid-3` (строки 134-135)
  - Адаптивные формы: `form-grid` (строки 92-93)

### Базовый шаблон
- **Файл:** `templates/base.html`
  - Viewport meta tag (строка 5): `<meta name="viewport" content="width=device-width, initial-scale=1.0" />`
  - Адаптивная навигация

---

## 6. ИНТЕГРАЦИЯ С БАЗОЙ ДАННЫХ

### Настройки БД
- **Файл:** `skillswap/settings.py` (строки 85-102)
  - PostgreSQL для продакшена (через `dj-database-url`)
  - SQLite для разработки
  - Автоматическое переключение по переменной `DATABASE_URL`

### Модели (ORM)
- **Файл:** `accounts/models.py`
  - Все модели используют Django ORM
  - Связи: ForeignKey, ManyToMany

### Миграции
- **Директория:** `accounts/migrations/`
  - 9 миграций, включая `0009_user_role.py` для ролей
- **Команды:** `python manage.py makemigrations`, `python manage.py migrate`

---

## 7. RESTful API ДЛЯ ВЗАИМОДЕЙСТВИЯ ФРОНТЕНДА И БЭКЕНДА

### API Views
- **Файл:** `accounts/api_views.py`
  - `UserListAPIView` (строки 20-35) - GET /api/users/
  - `UserDetailAPIView` (строки 38-42) - GET /api/users/{id}/
  - `SkillListAPIView` (строки 45-62) - GET/POST /api/skills/
  - `SkillDetailAPIView` (строки 65-70) - GET/PUT/DELETE /api/skills/{slug}/
  - `ExchangeRequestListAPIView` (строки 73-100) - GET/POST /api/exchanges/
  - `ExchangeRequestDetailAPIView` (строки 103-113) - GET/PUT/DELETE /api/exchanges/{id}/
  - `InboxRequestsAPIView` (строки 116-125) - GET /api/exchanges/inbox/
  - `exchange_action()` (строки 130-187) - POST /api/exchanges/{id}/action/
  - `api_login()` (строки 191-209) - POST /api/auth/login/
  - `api_logout()` (строки 212-220) - POST /api/auth/logout/

### API URLs
- **Файл:** `accounts/api_urls.py`
  - Все маршруты API зарегистрированы здесь

### Сериализаторы
- **Файл:** `accounts/serializers.py`
  - `UserSerializer` (строки 14-25)
  - `UserListSerializer` (строки 28-32)
  - `SkillSerializer` (строки 8-11)
  - `ExchangeRequestSerializer` (строки 35-47)
  - `ExchangeRequestCreateSerializer` (строки 50-53)
  - `ExchangeRequestActionSerializer` (строки 56-63)

### Настройки DRF
- **Файл:** `skillswap/settings.py` (строки 177-192)
  - Аутентификация: Session + Token
  - Пагинация: PageNumberPagination (20 элементов)
  - Разрешения по умолчанию

---

## 8. ВАЛИДАЦИЯ ДАННЫХ И ОБРАБОТКА ОШИБОК

### Валидация форм (клиентская и серверная)
- **Файл:** `accounts/forms.py`
  - `RegisterForm` - валидация регистрации
  - `ProfileForm` - валидация профиля (строки 45-51) - проверка наличия навыков
  - `ExchangeCreateForm` - валидация создания обмена
  - `ExchangeSendForm` - валидация отправки запроса

### Валидация сериализаторов (API)
- **Файл:** `accounts/serializers.py`
  - Все сериализаторы используют DRF валидацию
  - `ExchangeRequestActionSerializer` - кастомная валидация action (строки 60-63)

### Валидация паролей
- **Файл:** `skillswap/settings.py` (строки 108-121)
  - Django password validators настроены

### Обработка ошибок в API
- **Файл:** `accounts/api_views.py`
  - HTTP статусы: 400, 401, 403, 404
  - Примеры: строки 196-198, 208-209, 135-136, 140-141

### Обработка ошибок в представлениях
- **Файл:** `accounts/views.py`
  - Django messages framework для уведомлений пользователя
  - Примеры: строки 29, 43, 79, 113, 141, 159, 194, 210

---

## 9. ПОИСК И ФИЛЬТРАЦИЯ ОСНОВНЫХ ДАННЫХ

### Поиск пользователей
- **Файл:** `accounts/views.py`
  - Функция: `user_search()` (строки 221-257)
  - Поиск по: username, full_name, first_name, last_name
  - Фильтрация по навыкам (могут преподавать / хотят изучить)
- **URL:** `/accounts/users/`
- **Шаблон:** `templates/accounts/user_search.html`

### Поиск в API
- **Файл:** `accounts/api_views.py`
  - `UserListAPIView.get_queryset()` (строки 25-35)
  - Параметр: `?search=query`

### Фильтрация в админ-панели
- **Файл:** `accounts/admin_views.py`
  - `admin_users()` - поиск пользователей (строки 69-85)
  - `admin_exchanges()` - фильтрация по статусу (строки 124-140)

### Поиск в Django Admin
- **Файл:** `accounts/admin.py`
  - `search_fields` в UserAdmin, SkillAdmin, ExchangeRequestAdmin

---

## 10. СОРТИРОВКА И ПАГИНАЦИЯ ПРИ ВЫВОДЕ ДАННЫХ

### Пагинация в представлениях
- **Файл:** `accounts/views.py`
  - `user_search()` (строки 244-247) - Paginator, 12 элементов на страницу

### Пагинация в API
- **Файл:** `skillswap/settings.py` (строки 186-187)
  - `DEFAULT_PAGINATION_CLASS: 'rest_framework.pagination.PageNumberPagination'`
  - `PAGE_SIZE: 20`

### Сортировка
- **Файл:** `accounts/models.py`
  - `Skill.Meta.ordering = ["name"]` (строка 14)
  - `ExchangeRequest.Meta.ordering = ['-created_at']` (строка 72)
- **Файл:** `accounts/views.py`
  - `user_search()` - сортировка по username (строка 242)
- **Файл:** `accounts/api_views.py`
  - `UserListAPIView` - сортировка по username (строка 26)
  - `ExchangeRequestListAPIView` - сортировка по дате создания (строка 86)

---

## 11. ЛОГИРОВАНИЕ И МОНИТОРИНГ АКТИВНОСТИ СИСТЕМЫ

### Настройка логирования
- **Файл:** `skillswap/settings.py` (строки 240-310)
  - Конфигурация `LOGGING`:
    - Форматтеры: verbose, simple, json
    - Обработчики: console, file, error_file
    - Логгеры: django, django.request, django.security, accounts, core
  - Создание директории logs (строка 310)

### Логирование действий пользователей
- **Файл:** `accounts/views.py`
  - Импорт: `import logging` (строка 1)
  - Логгер: `logger = logging.getLogger('accounts')` (строка 13)
  - Логирование:
    - Регистрация (строка 28)
    - Создание обмена (строка 81)
    - Принятие обмена (строка 141)
    - Подтверждение обмена (строки 186, 193)

### Мониторинг запросов (Middleware)
- **Файл:** `skillswap/middleware.py`
  - Класс: `RequestLoggingMiddleware` (строки 11-33)
  - Логирует медленные запросы (>1 сек) и ошибки (>=400)
- **Интеграция:** `skillswap/settings.py` (строка 92)

### Интеграция Sentry
- **Файл:** `skillswap/settings.py` (строки 19-38)
  - Условная инициализация при наличии `SENTRY_DSN`
  - Интеграции: DjangoIntegration, LoggingIntegration

---

## 12. АВТОМАТИЗИРОВАННОЕ ТЕСТИРОВАНИЕ (unit + integration)

### Unit тесты
- **Файл:** `accounts/tests.py`
  - `SkillSlugTests` (строки 11-27) - тесты генерации slug
  - `ExchangeRequestModelTests` (строки 30-101) - тесты модели обмена
  - `ExchangeViewsTests` (строки 104-152) - тесты представлений

### Интеграционные тесты API
- **Файл:** `accounts/tests_api.py`
  - `APIAuthenticationTests` (строки 10-48) - тесты аутентификации
  - `APIUserTests` (строки 51-85) - тесты API пользователей
  - `APISkillTests` (строки 88-125) - тесты API навыков
  - `APIExchangeRequestTests` (строки 128-220) - тесты API обменов

### Запуск тестов
- Команда: `python manage.py test`
- Для интеграционных: `python manage.py test accounts.tests_api`

---

## 13. БЕЗОПАСНОСТЬ (хэширование паролей, санитизация ввода, защита от SQL-инъекций/XSS/CSRF)

### Хэширование паролей
- **Автоматически:** Django использует PBKDF2 через `AbstractUser`
- **Настройки:** `skillswap/settings.py` (строки 108-121) - password validators

### CSRF защита
- **Файл:** `skillswap/settings.py` (строка 88)
  - Middleware: `'django.middleware.csrf.CsrfViewMiddleware'`
- **В шаблонах:** `{% csrf_token %}` используется в формах

### XSS защита
- **Автоматически:** Django templates экранизируют переменные
- **Пример:** `templates/base.html` - все переменные экранизируются автоматически

### SQL-инъекции защита
- **Автоматически:** Django ORM защищает от SQL-инъекций
- **Все запросы:** используют ORM методы (filter, get, etc.)

### Настройки безопасности для продакшена
- **Файл:** `skillswap/settings.py` (строки 50-62)
  - `ALLOWED_HOSTS` - через переменные окружения
  - `SECURE_SSL_REDIRECT` - редирект на HTTPS
  - `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE` - безопасные cookies
  - `SECURE_BROWSER_XSS_FILTER` - XSS фильтр браузера
  - `SECURE_CONTENT_TYPE_NOSNIFF` - защита от MIME sniffing
  - `X_FRAME_OPTIONS = 'DENY'` - защита от clickjacking
  - `SECURE_HSTS_SECONDS` - HSTS заголовки

---

## 14. ДЕПЛОЙ НА ОБЛАЧНУЮ ПЛАТФОРМУ

### Render
- **Файл:** `render.yaml`
  - Конфигурация для деплоя на Render
  - Настройки: buildCommand, startCommand, envVars

### Heroku
- **Файл:** `Procfile`
  - Команда запуска: `web: gunicorn skillswap.wsgi:application`

### Скрипт сборки
- **Файл:** `build.sh`
  - Установка зависимостей
  - Сборка статических файлов
  - Применение миграций

### Версия Python
- **Файл:** `runtime.txt`
  - Указана версия Python для деплоя

### Настройки для продакшена
- **Файл:** `skillswap/settings.py`
  - Поддержка PostgreSQL через `dj-database-url`
  - WhiteNoise для статических файлов (строки 145-149)

---

## 15. ДОКУМЕНТАЦИЯ

### README
- **Файл:** `README.md`
  - Описание проекта
  - Инструкции по установке
  - Структура проекта
  - Используемые технологии

### Руководство пользователя
- **Файл:** `USER_GUIDE.md`
  - Подробное руководство для пользователей (220 строк)
  - Регистрация, работа с профилем, обмены, API

### Документация по мониторингу
- **Файл:** `MONITORING.md`
  - Настройка Sentry
  - Локальное логирование
  - Мониторинг запросов

### API документация (Swagger/OpenAPI)
- **URL:** `/swagger/` - Swagger UI
- **URL:** `/redoc/` - ReDoc
- **Файл:** `skillswap/urls.py` (строки 25-36, 44-46)
- **Аннотации:** `accounts/api_views.py` - Swagger аннотации в API views

---

## 16. КОНТЕЙНЕРИЗАЦИЯ С ПОМОЩЬЮ DOCKER

### Dockerfile
- **Файл:** `Dockerfile`
  - Базовый образ: Python 3.12-slim
  - Установка зависимостей
  - Копирование проекта
  - Сборка статических файлов
  - Команда запуска: gunicorn

### Docker Compose
- **Файл:** `docker-compose.yml`
  - Сервис `web` - Django приложение
  - Сервис `db` - PostgreSQL 16
  - Volumes для данных и статики

### Запуск
- Команда: `docker-compose up -d`

---

## 17. CI/CD PIPELINE

### GitHub Actions
- **Файл:** `.github/workflows/ci.yml`
  - Job `test` (строки 14-67):
    - Запуск тестов с PostgreSQL
    - Покрытие кода (coverage)
  - Job `lint` (строки 69-95):
    - flake8, black, isort
  - Job `security` (строки 97-120):
    - bandit, safety
  - Job `build-docker` (строки 122-140):
    - Сборка Docker образа

### Триггеры
- Push в main/master/develop
- Pull Request в main/master/develop

---

## 18. МОНИТОРИНГ И ЛОГИРОВАНИЕ

### Sentry (мониторинг ошибок)
- **Файл:** `skillswap/settings.py` (строки 19-38)
  - Условная инициализация через `SENTRY_DSN`
  - Интеграции: Django, Logging

### Логирование (см. критерий 11)
- **Файл:** `skillswap/settings.py` (строки 240-310)
- **Файл:** `skillswap/middleware.py` - мониторинг запросов

### Документация
- **Файл:** `MONITORING.md` - инструкции по настройке

---

## 19. НАГРУЗОЧНОЕ ТЕСТИРОВАНИЕ

### Скрипты k6
- **Файл:** `load_tests/k6_basic.js`
  - Базовый нагрузочный тест
  - Постепенное увеличение нагрузки до 30 пользователей
- **Файл:** `load_tests/k6_stress.js`
  - Стресс-тест до 200 пользователей
  - Параллельные запросы

### Документация
- **Файл:** `load_tests/README.md`
  - Инструкции по установке k6
  - Команды запуска
  - Описание тестов
  - Интерпретация результатов

### Запуск
- Команда: `k6 run load_tests/k6_basic.js`

---

## ДОПОЛНИТЕЛЬНЫЕ КОМПОНЕНТЫ

### Админ-панель приложения (критерий 4)
- **Файлы:** `accounts/admin_views.py`, `templates/admin/*.html`
- **URL:** `/accounts/admin-panel/`

### Роли пользователей (критерий 2)
- **Файлы:** `accounts/models.py`, `accounts/permissions.py`
- **Миграция:** `accounts/migrations/0009_user_role.py`

### Руководство пользователя (критерий 15)
- **Файл:** `USER_GUIDE.md`

---

## БЫСТРАЯ НАВИГАЦИЯ ПО ФАЙЛАМ

### Основные директории:
```
skill-swap/
├── accounts/              # Основное приложение
│   ├── models.py         # Модели данных
│   ├── views.py          # Представления (views)
│   ├── api_views.py     # API endpoints
│   ├── admin_views.py   # Админ-панель приложения
│   ├── forms.py          # Формы
│   ├── serializers.py    # API сериализаторы
│   ├── permissions.py    # Кастомные разрешения
│   ├── tests.py          # Unit тесты
│   ├── tests_api.py      # Интеграционные тесты
│   ├── admin.py          # Django Admin
│   ├── urls.py           # URL маршруты
│   └── api_urls.py       # API URL маршруты
├── core/                 # Основная функциональность
├── skillswap/            # Настройки проекта
│   ├── settings.py       # Все настройки
│   ├── urls.py           # Главные URL маршруты
│   └── middleware.py     # Middleware для мониторинга
├── templates/            # HTML шаблоны
│   ├── accounts/         # Шаблоны аккаунтов
│   ├── admin/            # Шаблоны админ-панели
│   └── exchanges/        # Шаблоны обменов
├── static/               # Статические файлы
│   └── css/style.css     # Стили (адаптивные)
├── .github/workflows/    # CI/CD
│   └── ci.yml            # GitHub Actions
├── load_tests/           # Нагрузочное тестирование
│   ├── k6_basic.js       # Базовый тест
│   ├── k6_stress.js      # Стресс-тест
│   └── README.md         # Документация
└── docs/                 # Документация
    ├── README.md         # Основная документация
    ├── USER_GUIDE.md     # Руководство пользователя
    └── MONITORING.md     # Мониторинг
```

---

**Последнее обновление:** 2024  
**Версия:** 1.0

