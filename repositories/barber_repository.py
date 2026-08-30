"""Data-access layer for the Barber aggregate, including its working hours."""

from models.models import Barber, WorkingHours

from .base_repository import BaseRepository


class BarberRepository(BaseRepository):
    model = Barber

    def active(self):
        return self.list(is_active=True)

    def create(self, specialty_ids=None, **fields) -> Barber:
        barber = Barber(**fields)
        self.save(barber)
        if specialty_ids:
            barber.specialties.set(specialty_ids)
        return barber

    def set_working_hours(
        self, barber: Barber, week_day: int, start_time, end_time
    ) -> WorkingHours:
        working_hours, _ = WorkingHours.objects.update_or_create(
            barber=barber,
            week_day=week_day,
            defaults={"start_time": start_time, "end_time": end_time},
        )
        working_hours.full_clean()
        return working_hours
