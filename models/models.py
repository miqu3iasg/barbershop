"""
Re-exports every domain entity so that (a) Django's app registry can find
them via the conventional "<app>.models" import path, and (b) the rest of
the codebase can simply do `from models import Client, Barber, ...`.
"""

from .appointment import Appointment, AppointmentStatus
from .appointment_item import AppointmentItem
from .barber import Barber
from .client import Client
from .service import Service
from .working_hours import WeekDay, WorkingHours

__all__ = [
    "Appointment",
    "AppointmentStatus",
    "AppointmentItem",
    "Barber",
    "Client",
    "Service",
    "WeekDay",
    "WorkingHours",
]
