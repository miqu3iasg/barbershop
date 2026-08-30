"""
AppointmentItem: the line item linking an Appointment to a Service.

Stores a *snapshot* of the service's price/duration at booking time, so a
future price change on the Service catalog never retroactively changes the
value of appointments already scheduled.
"""
from django.db import models


class AppointmentItem(models.Model):
    appointment = models.ForeignKey("models.Appointment", related_name="items", on_delete=models.CASCADE)
    service = models.ForeignKey("models.Service", related_name="appointment_items", on_delete=models.PROTECT)
    quantity = models.PositiveSmallIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=8, decimal_places=2)
    duration_minutes = models.PositiveIntegerField()

    class Meta:
        app_label = "models"
        unique_together = ("appointment", "service")
        verbose_name = "Appointment item"
        verbose_name_plural = "Appointment items"

    def __str__(self) -> str:
        return f"{self.service.name} x{self.quantity}"

    @classmethod
    def build_for(cls, appointment, service, quantity: int = 1) -> "AppointmentItem":
        """Domain factory: creates an (unsaved) item snapshotting the service's current price/duration."""
        return cls(
            appointment=appointment,
            service=service,
            quantity=quantity,
            unit_price=service.price_for(quantity=1),
            duration_minutes=service.duration_for(quantity=1),
        )
