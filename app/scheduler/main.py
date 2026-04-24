"""Планировщик фоновых задач (APScheduler).

Запуск: python -m app.scheduler.main
"""
from __future__ import annotations

import asyncio
import signal

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from app.common.config import get_settings
from app.common.logger import configure_logging, get_logger
from app.scheduler.jobs import followup, monthly_invoices, reminders, seasonal

log = get_logger("scheduler")


def build_scheduler() -> AsyncIOScheduler:
    settings = get_settings()
    sched = AsyncIOScheduler(timezone=settings.tz)

    # Проверка follow-up каждые 15 минут
    sched.add_job(
        followup.check_silent_dialogs,
        trigger=IntervalTrigger(minutes=15),
        id="followup_check",
        replace_existing=True,
    )

    # Напоминания о завтрашних занятиях каждый день в 18:00 местного
    sched.add_job(
        reminders.remind_tomorrow,
        trigger=CronTrigger(hour=18, minute=0, timezone=settings.tz),
        id="lesson_reminders",
        replace_existing=True,
    )

    # Генерация месячных счетов 1 числа в 10:00
    if settings.feature_auto_invoice:
        sched.add_job(
            monthly_invoices.generate_monthly,
            trigger=CronTrigger(day=1, hour=10, minute=0, timezone=settings.tz),
            id="monthly_invoices",
            replace_existing=True,
        )

    # Сезонные поздравления — крон ежедневно в 9:00, внутри решает что слать
    sched.add_job(
        seasonal.send_daily_triggers,
        trigger=CronTrigger(hour=9, minute=0, timezone=settings.tz),
        id="seasonal_triggers",
        replace_existing=True,
    )

    return sched


async def run() -> None:
    configure_logging()
    sched = build_scheduler()
    sched.start()
    log.info("scheduler_started", jobs=[j.id for j in sched.get_jobs()])

    # Держим процесс живым
    stop = asyncio.Event()
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, stop.set)
        except NotImplementedError:
            # Windows
            pass
    await stop.wait()

    sched.shutdown(wait=True)
    log.info("scheduler_stopped")


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()
