"""Все SQLAlchemy-модели. Импорт в одном месте — для автодискавери Alembic."""
from app.db.models.admin import Admin
from app.db.models.anketa import Anketa
from app.db.models.audit import AuditLog
from app.db.models.broadcast import Broadcast
from app.db.models.child import Child
from app.db.models.client import Client
from app.db.models.diagnostic import Diagnostic
from app.db.models.dialog import Dialog
from app.db.models.lesson import Lesson
from app.db.models.message import Message
from app.db.models.payment import Payment
from app.db.models.specialist import Specialist
from app.db.models.task import Task
from app.db.models.template import Template

__all__ = [
    "Admin",
    "Anketa",
    "AuditLog",
    "Broadcast",
    "Child",
    "Client",
    "Diagnostic",
    "Dialog",
    "Lesson",
    "Message",
    "Payment",
    "Specialist",
    "Task",
    "Template",
]
