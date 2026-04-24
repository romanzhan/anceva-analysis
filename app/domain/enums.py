"""Перечисления предметной области.

Все enum'ы — StrEnum, чтобы SQLAlchemy хранил их как строки (читаемо в БД).
"""
from __future__ import annotations

from enum import StrEnum


class ClientState(StrEnum):
    """Статус клиента (родителя) в воронке."""

    NEW = "new"                  # написал впервые, ещё не квалифицирован
    QUALIFYING = "qualifying"    # идёт диалог квалификации
    BOOKED = "booked"            # диагностика оплачена и назначена
    ACTIVE = "active"            # ходит на занятия
    PAUSED = "paused"            # временный перерыв
    LOST = "lost"                # 30+ дней молчания
    RETURNING = "returning"      # вернулся после паузы, нужен админ


class DialogMode(StrEnum):
    BOT = "bot"
    ADMIN = "admin"


class DialogStage(StrEnum):
    """Текущее состояние FSM. Ветви описаны в TECH.html §06."""

    GREETING = "greeting"
    GOT_PARENT_NAME = "got_parent_name"
    GOT_AGE = "got_age"
    BRANCHING = "branching"
    COLLECTING = "collecting"
    PRESENTING_DI = "presenting_di"
    PICKING_SLOT = "picking_slot"
    GETTING_CHILD_INFO = "getting_child_info"
    INVOICING = "invoicing"
    AWAITING_CHECK = "awaiting_check"
    BOOKED = "booked"
    SENT_ANKETA = "sent_anketa"
    ANKETA_FILLED = "anketa_filled"
    PRE_REMINDER = "pre_reminder"
    DI_DONE = "di_done"
    ACTIVE = "active"
    PAUSED = "paused"
    LOST = "lost"
    RETURNING = "returning"
    ESCALATED = "escalated"


class Direction(StrEnum):
    """Направления работы центра."""

    SPEECH_LAUNCH = "speech_launch"        # запуск речи (1–3)
    DEFECTOLOGIST = "defectologist"        # дефектолог (2–5)
    ARTICULATION = "articulation"          # постановка звуков / грамматика (4–7)
    SCHOOL_PREP = "school_prep"            # подготовка к школе (5–7)
    MOTHER_CHILD = "mother_child"          # Мама+малыш (1–3)
    AFK = "afk"                            # адаптивная физкультура
    NEURO = "neuro"                        # нейропсихолог (школьники)
    STUTTERING = "stuttering"              # заикание
    GROUP_CORRECTIONAL = "group_correctional"  # коррекционные мини-группы
    MASSAGE = "massage"                    # логопедический массаж


class AgeBand(StrEnum):
    INFANT = "0_2"           # 0–2 года
    TODDLER = "2_5"          # 2–5 лет
    PRESCHOOL = "4_6"        # 4–6 лет
    PRE_SCHOOL = "5_7"       # 5–7 лет (группа ПШ)
    SCHOOL = "7_13"          # школьник
    TEEN = "14_16"           # подросток (особый контур)


class LessonStatus(StrEnum):
    PLANNED = "planned"
    DONE = "done"
    MISSED_EXCUSED = "missed_excused"       # предупредили до 19:00 → перерасчёт
    MISSED_UNEXCUSED = "missed_unexcused"   # день-в-день → засчитано, не отрабатывается
    RESCHEDULED = "rescheduled"
    CANCELLED = "cancelled"


class DiagnosticStatus(StrEnum):
    BOOKED = "booked"
    DONE = "done"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class PaymentStatus(StrEnum):
    DRAFT = "draft"           # черновик, не отправлен
    INVOICED = "invoiced"     # счёт отправлен клиенту
    PARTIAL = "partial"       # частично оплачено
    PAID = "paid"             # полностью оплачено
    OVERDUE = "overdue"       # просрочено


class PaymentMethod(StrEnum):
    CASH = "cash"
    KASPI = "kaspi"
    TRANSFER = "transfer"     # редко, из-за границы


class MessageDirection(StrEnum):
    IN = "in"    # от клиента нам
    OUT = "out"  # от нас клиенту


class MessageSender(StrEnum):
    CLIENT = "client"
    BOT = "bot"
    ADMIN = "admin"
    SYSTEM = "system"


class MessageType(StrEnum):
    TEXT = "text"
    VOICE = "voice"
    AUDIO = "audio"
    PHOTO = "photo"
    VIDEO = "video"
    DOCUMENT = "document"
    STICKER = "sticker"
    SYSTEM = "system"


class AdminRole(StrEnum):
    OWNER = "owner"           # Мария Сергеевна
    ADMIN = "admin"           # Агния и другие админы
    METHODIST = "methodist"   # Маргарита Наильевна
    SPECIALIST = "specialist"  # педагоги, видят только своих


class TaskKind(StrEnum):
    """Виды отложенных задач для scheduler."""

    FOLLOWUP_24H = "followup_24h"
    FOLLOWUP_48H = "followup_48h"
    FOLLOWUP_7D = "followup_7d"
    REACTIVATE_30D = "reactivate_30d"
    LESSON_REMINDER = "lesson_reminder"
    DI_REMINDER = "di_reminder"
    ANKETA_REMINDER = "anketa_reminder"
    MONTHLY_INVOICE = "monthly_invoice"
    PAYMENT_NAG = "payment_nag"
    BIRTHDAY = "birthday"
    SEASONAL = "seasonal"


class TaskStatus(StrEnum):
    PENDING = "pending"
    DONE = "done"
    CANCELLED = "cancelled"
    FAILED = "failed"


class Source(StrEnum):
    """Источник первого обращения."""

    DIRECT = "direct"
    GIS_2 = "2gis"
    INSTAGRAM = "instagram"
    REFERRAL = "referral"
    DOCTOR = "doctor"
    RETURNING = "returning"
    UNKNOWN = "unknown"


class Language(StrEnum):
    RU = "ru"
    KZ = "kz"
    RU_KZ = "ru_kz"
