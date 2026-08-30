"""Application service for Barber use-cases, including working-hours management."""

from typing import Optional

from models.models import Barber, WorkingHours
from repositories.barber_repository import BarberRepository


class BarberService:
    def __init__(self, repository: Optional[BarberRepository] = None):
        self.repository = repository or BarberRepository()

    def list_barbers(self, is_active: Optional[bool] = None):
        filters = {} if is_active is None else {"is_active": is_active}
        return self.repository.list(**filters)

    def register_barber(self, specialty_ids=None, **fields) -> Barber:
        return self.repository.create(specialty_ids=specialty_ids, **fields)

    def set_working_hours(
        self, barber: Barber, week_day: int, start_time, end_time
    ) -> WorkingHours:
        return self.repository.set_working_hours(barber, week_day, start_time, end_time)
