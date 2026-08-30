"""Application service for the appointment scheduling use-case: the one
that coordinates the most entities (client, barber, N services)."""

from typing import Optional

from exceptions.domain_exceptions import ResourceNotFoundError
from models.models import Appointment
from repositories.appointment_repository import AppointmentRepository
from repositories.barber_repository import BarberRepository
from repositories.client_repository import ClientRepository
from repositories.service_repository import ServiceRepository


class AppointmentService:
    def __init__(
        self,
        appointment_repository: Optional[AppointmentRepository] = None,
        client_repository: Optional[ClientRepository] = None,
        barber_repository: Optional[BarberRepository] = None,
        service_repository: Optional[ServiceRepository] = None,
    ):
        self.appointment_repository = appointment_repository or AppointmentRepository()
        self.client_repository = client_repository or ClientRepository()
        self.barber_repository = barber_repository or BarberRepository()
        self.service_repository = service_repository or ServiceRepository()

    def list_appointments(self, **filters):
        return self.appointment_repository.list(**filters)

    def schedule_appointment(
        self, *, client_id, barber_id, start_at, service_ids, notes=""
    ) -> Appointment:
        client = self.client_repository.get_by_id(client_id)
        if client is None:
            raise ResourceNotFoundError("Client not found.")

        barber = self.barber_repository.get_by_id(barber_id)
        if barber is None:
            raise ResourceNotFoundError("Barber not found.")

        services = list(
            self.service_repository.get_queryset().filter(
                id__in=service_ids, is_active=True
            )
        )

        return self.appointment_repository.schedule(
            client=client,
            barber=barber,
            start_at=start_at,
            services=services,
            notes=notes,
        )

    def cancel_appointment(self, appointment_id) -> Appointment:
        appointment = self.appointment_repository.get_by_id(appointment_id)

        if appointment is None:
            raise ResourceNotFoundError("Appointment not found.")

        return self.appointment_repository.cancel(appointment)

    def confirm_appointment(self, appointment_id) -> Appointment:
        appointment = self.appointment_repository.get_by_id(appointment_id)

        if appointment is None:
            raise ResourceNotFoundError("Appointment not found.")

        return self.appointment_repository.confirm(appointment)
