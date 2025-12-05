# Нагрузочное тестирование SkillSwap

## Установка k6

### Windows
```bash
choco install k6
```

### macOS
```bash
brew install k6
```

### Linux
```bash
sudo gpg -k
sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update
sudo apt-get install k6
```

## Запуск тестов

### Базовый нагрузочный тест
```bash
k6 run load_tests/k6_basic.js
```

### Стресс-тест
```bash
k6 run load_tests/k6_stress.js
```

### С кастомными параметрами
```bash
k6 run --env BASE_URL=http://your-server.com --env TEST_USERNAME=user --env TEST_PASSWORD=pass load_tests/k6_basic.js
```

## Описание тестов

### k6_basic.js
Базовый нагрузочный тест с постепенным увеличением нагрузки:
- Разогрев: 10 пользователей за 30 секунд
- Нормальная нагрузка: 20 пользователей
- Пиковая нагрузка: 30 пользователей
- Возврат к нормальной нагрузке

Тестирует основные endpoints:
- `/api/users/` - список пользователей
- `/api/users/?search=test` - поиск пользователей
- `/api/skills/` - список навыков
- `/api/exchanges/` - список обменов

### k6_stress.js
Стресс-тест для определения максимальной нагрузки:
- Постепенное увеличение до 200 одновременных пользователей
- Параллельные запросы к нескольким endpoints
- Определение точки отказа системы

## Метрики

Тесты отслеживают:
- **http_req_duration** - время ответа запросов
- **http_req_failed** - процент неудачных запросов
- **errors** - кастомная метрика ошибок

## Пороговые значения

- 95% запросов должны быть быстрее 500ms (базовый тест) или 1000ms (стресс-тест)
- Меньше 1-5% ошибок в зависимости от теста

## Интерпретация результатов

После запуска теста вы увидите:
- Общее количество запросов
- Среднее время ответа
- Процент ошибок
- Распределение времени ответа (p50, p90, p95, p99)

Если тест не проходит пороговые значения, необходимо:
1. Оптимизировать запросы к базе данных
2. Добавить кэширование
3. Масштабировать приложение

