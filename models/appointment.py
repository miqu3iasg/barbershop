"""
Appointment domain model, the aggregate root of the scheduling process.

Every scheduling business rule (computing the end time, validating working
hours, detecting conflicts, and the cancel/confirm state machine) lives
here as a method on the model itself, not scattered across services or
views. The repository/service layers only decide *when* to call these
methods and handle persistence; they never reimplement the rules.
"""

from datetime import timedelta
from decimal import Decimal

from django.db import models
from django.utils import timezone

from exceptions.domain_exceptions import (
    BarberNotAvailableError,
    EmptyServiceListError,
    InvalidStatusTransitionError,
    OutsideWorkingHoursError,
    PastSchedulingError,
    SchedulingConflictError,
)


class AppointmentStatus(models.TextChoices):
    SCHEDULED = "SCHEDULED", "Scheduled"
    CONFIRMED = "CONFIRMED", "Confirmed"
    IN_PROGRESS = "IN_PROGRESS", "In progress"
    COMPLETED = "COMPLETED", "Completed"
    CANCELLED = "CANCELLED", "Cancelled"
    NO_SHOW = "NO_SHOW", "No-show"


# Statuses that free up the barber's agenda (they don't block new bookings).
NON_BLOCKING_STATUSES = [AppointmentStatus.CANCELLED, AppointmentStatus.NO_SHOW]
# Statuses that can no longer be cancelled.
FINAL_STATUSES = [AppointmentStatus.COMPLETED, AppointmentStatus.CANCELLED]


class AppointmentQuerySet(models.QuerySet):
    """Query helpers used by the conflict-detection rule below."""

    def for_barber(self, barber):
        return self.filter(barber=barber)

    def overlapping(self, start_at, end_at):
        return self.filter(start_at__lt=end_at, end_at__gt=start_at)

    def blocking(self):
        return self.exclude(status__in=NON_BLOCKING_STATUSES)


class Appointment(models.Model):
    client = models.ForeignKey(
        "models.Client", related_name="appointments", on_delete=models.PROTECT
    )
    barber = models.ForeignKey(
        "models.Barber", related_name="appointments", on_delete=models.PROTECT
    )
    start_at = models.DateTimeField()
    end_at = models.DateTimeField(editable=False)
    status = models.CharField(
        max_length=20,
        choices=AppointmentStatus.choices,
        default=AppointmentStatus.SCHEDULED,
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = AppointmentQuerySet.as_manager()

    class Meta:
        app_label = "models"
        ordering = ["-start_at"]
        verbose_name = "Appointment"
        verbose_name_plural = "Appointments"

    def __str__(self) -> str:
        return f"Appointment #{self.pk} - {self.client.name} with {self.barber.name}"

    # Scheduling rule

    def schedule(self, services) -> None:
        """
        Domain rule for booking: computes the end time from the chosen
        services and validates it against the barber's working hours and
        existing agenda. Raises a DomainError subclass on any violation.
        Does not persist anything — persistence is the repository's job.
        """
        if not services:
            raise EmptyServiceListError("At least one service must be selected.")
        if self.start_at < timezone.now():
            raise PastSchedulingError("Cannot schedule an appointment in the past.")

        total_minutes = sum(service.duration_minutes for service in services)
        self.end_at = self.start_at + timedelta(minutes=total_minutes)

        self._ensure_within_working_hours()
        self._ensure_no_conflicts()

    def _ensure_within_working_hours(self) -> None:
        working_hours = self.barber.working_hours_for(self.start_at.weekday())
        if working_hours is None:
            raise BarberNotAvailableError(
                f"{self.barber.name} does not work on this day of the week."
            )
        if not working_hours.covers(self.start_at.time(), self.end_at.time()):
            raise OutsideWorkingHoursError(
                f"Outside {self.barber.name}'s working hours "
                f"({working_hours.start_time.strftime('%H:%M')} - {working_hours.end_time.strftime('%H:%M')})."
            )

    def _ensure_no_conflicts(self) -> None:
        conflicts = (
            Appointment.objects.for_barber(self.barber)
            .overlapping(self.start_at, self.end_at)
            .blocking()
            .exclude(pk=self.pk)
        )
        if conflicts.exists():
            raise SchedulingConflictError(
                "This barber already has an appointment at this time."
            )

    # Status state machine

    def confirm(self) -> None:
        """Domain rule: only a freshly scheduled appointment can be confirmed."""
        if self.status != AppointmentStatus.SCHEDULED:
            raise InvalidStatusTransitionError(
                "Only a scheduled appointment can be confirmed."
            )
        self.status = AppointmentStatus.CONFIRMED

    def cancel(self) -> None:
        """Domain rule: completed or already-cancelled appointments cannot be cancelled again."""
        if self.status in FINAL_STATUSES:
            raise InvalidStatusTransitionError(
                f"An appointment with status '{self.status}' cannot be cancelled."
            )
        self.status = AppointmentStatus.CANCELLED

    # Derived values

    def total_price(self) -> Decimal:
        return sum(
            (item.unit_price * item.quantity for item in self.items.all()),
            start=Decimal("0.00"),
        )

    def total_duration_minutes(self) -> int:
        return sum(item.duration_minutes for item in self.items.all())
