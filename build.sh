#!/usr/bin/env bash
# Выходим при первой ошибке
set -o errexit

# Устанавливаем зависимости
pip install -r requirements.txt

# Собираем статические файлы
python manage.py collectstatic --noinput

# Применяем миграции
python manage.py migrate
