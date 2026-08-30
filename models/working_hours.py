"""WorkingHours domain model, a barber's shift for a given weekday."""

from datetime import time

from django.core.exceptions import ValidationError
from django.db import models


class WeekDay(models.IntegerChoices):
    MONDAY = 0, "Monday"
    TUESDAY = 1, "Tuesday"
    WEDNESDAY = 2, "Wednesday"
    THURSDAY = 3, "Thursday"
    FRIDAY = 4, "Friday"
    SATURDAY = 5, "Saturday"
    SUNDAY = 6, "Sunday"


class WorkingHours(models.Model):
    barber = models.ForeignKey(
        "models.Barber", related_name="working_hours", on_delete=models.CASCADE
    )
    week_day = models.IntegerField(choices=WeekDay.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        app_label = "models"
        unique_together = ("barber", "week_day")
        ordering = ["week_day", "start_time"]
        verbose_name = "Working hours"
        verbose_name_plural = "Working hours"

    def __str__(self) -> str:
        return f"{self.barber.name} - {self.get_week_day_display()} {self.start_time}-{self.end_time}"

    def clean(self) -> None:
        if self.start_time >= self.end_time:
            raise ValidationError("start_time must be before end_time.")

    def covers(self, start: time, end: time) -> bool:
        """Domain rule: whether a [start, end) time window fits entirely within this shift."""

        return self.start_time <= start and end <= self.end_time
