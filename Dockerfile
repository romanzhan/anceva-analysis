FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    tini \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Зависимости — отдельным слоем для кэша
COPY pyproject.toml ./
RUN pip install --upgrade pip && pip install -e "."

# Код
COPY app ./app
COPY migrations ./migrations
COPY alembic.ini ./alembic.ini
COPY Procfile ./Procfile

# Папка для SQLite / временных файлов
RUN mkdir -p /app/var

# honcho как process manager внутри контейнера
RUN pip install honcho

EXPOSE 8000
ENV PORT=8000

# tini обрабатывает сигналы и зомби-процессы
ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["honcho", "start"]
