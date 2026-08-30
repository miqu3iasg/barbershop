"""
Persistence for the Appointment aggregate.

Business rules (conflict detection, working-hours validation, status
transitions) live on the Appointment model itself. This repository is only
responsible for wiring the database transaction and persisting the
aggregate together with its line items.
"""
from django.db import transaction

from models.models import Appointment, AppointmentItem

from .base_repository import BaseRepository


class AppointmentRepository(BaseRepository):
    model = Appointment

    def get_queryset(self):
        return super().get_queryset().select_related("client", "barber").prefetch_related("items__service")

    @transaction.atomic
    def schedule(self, *, client, barber, start_at, services, notes="") -> Appointment:
        appointment = Appointment(client=client, barber=barber, start_at=start_at, notes=notes)
        appointment.schedule(services)  # domain validation lives on the model
        appointment.save()

        items = [AppointmentItem.build_for(appointment, service) for service in services]
        AppointmentItem.objects.bulk_create(items)
        return appointment

    @transaction.atomic
    def cancel(self, appointment: Appointment) -> Appointment:
        appointment.cancel()
        appointment.save(update_fields=["status", "updated_at"])
        return appointment

    @transaction.atomic
    def confirm(self, appointment: Appointment) -> Appointment:
        appointment.confirm()
        appointment.save(update_fields=["status", "updated_at"])
        return appointment
