# Anceva Bot — команды разработчика.
# Установи just (https://github.com/casey/just) или используй `python -m scripts.run`.

set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]
set dotenv-load := true

default:
    @just --list

# --- Setup --------------------------------------------------------------------

install:
    python -m pip install -e ".[dev]"

venv:
    python -m venv .venv

# --- Database -----------------------------------------------------------------

db-upgrade:
    alembic upgrade head

db-down:
    alembic downgrade -1

db-rev message:
    alembic revision --autogenerate -m "{{message}}"

db-reset:
    rm -f ./var/anceva.sqlite
    alembic upgrade head

# --- Run ----------------------------------------------------------------------

bot:
    python -m app.bot.main

admin-bot:
    python -m app.admin_bot.main

web:
    uvicorn app.web.main:app --host 0.0.0.0 --port 8000 --reload

scheduler:
    python -m app.scheduler.main

# Все процессы сразу через honcho (локальная разработка)
run:
    honcho start -f Procfile.dev

# --- Quality ------------------------------------------------------------------

lint:
    ruff check app tests

fmt:
    ruff check --fix app tests
    black app tests

typecheck:
    mypy app

test:
    pytest

test-cov:
    pytest --cov=app --cov-report=term-missing --cov-report=html

check: lint typecheck test
