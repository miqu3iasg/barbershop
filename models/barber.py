"""Barber domain model."""

from django.db import models


class Barber(models.Model):
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    hired_at = models.DateField()
    is_active = models.BooleanField(default=True)
    specialties = models.ManyToManyField(
        "models.Service",
        related_name="barbers",
        blank=True,
        help_text="Services this barber is qualified to perform. Empty means 'any service'.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "models"
        ordering = ["name"]
        verbose_name = "Barber"
        verbose_name_plural = "Barbers"

    def __str__(self) -> str:
        return self.name

    def is_qualified_for(self, service) -> bool:
        """Domain rule: a barber with no registered specialties is treated as a generalist."""

        return (
            not self.specialties.exists()
            or self.specialties.filter(pk=service.pk).exists()
        )

    def working_hours_for(self, week_day: int):
        """Domain lookup: this barber's shift for a given day of the week, if any."""

        return self.working_hours.filter(week_day=week_day).first()

    def deactivate(self) -> None:
        self.is_active = False
