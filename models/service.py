"""Service domain model, a procedure offered by the barbershop (e.g. haircut, beard trim)."""

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models


class Service(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    duration_minutes = models.PositiveIntegerField(
        validators=[MinValueValidator(5)],
        help_text="Estimated duration of the service, in minutes.",
    )

    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "models"
        ordering = ["name"]
        verbose_name = "Service"
        verbose_name_plural = "Services"

    def __str__(self) -> str:
        return f"{self.name} ({self.duration_minutes}min - R$ {self.price})"

    def price_for(self, quantity: int = 1) -> Decimal:
        """Domain rule: total price for N units of this service."""

        return self.price * quantity

    def duration_for(self, quantity: int = 1) -> int:
        """Domain rule: total duration, in minutes, for N units of this service."""

        return self.duration_minutes * quantity
