# Python base image
FROM python:3.12-slim

# Prevent Python from writing .pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Workdir
WORKDIR /app

# System deps
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app

# Collect static at build time (optional, can also be done in entrypoint)
RUN python manage.py collectstatic --noinput || true

# Expose port
EXPOSE 8000

# Default envs (can be overridden)
ENV DJANGO_DEBUG=False \
    DJANGO_SECRET_KEY=changeme-in-production

# Run gunicorn
CMD ["gunicorn", "skillswap.wsgi:application", "--bind", "0.0.0.0:8000"]
