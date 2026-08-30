"""Client domain model, a barbershop customer who can book appointments."""

import re

from django.core.exceptions import ValidationError
from django.db import models


class Client(models.Model):
    name = models.CharField(max_length=150)
    document_number = models.CharField(
        max_length=11,
        unique=True,
        help_text="CPF, digits only (11 characters).",
    )
    phone = models.CharField(max_length=15)
    email = models.EmailField(unique=True)
    birth_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "models"
        ordering = ["name"]
        verbose_name = "Client"
        verbose_name_plural = "Clients"

    def __str__(self) -> str:
        return f"{self.name} ({self.document_number})"

    def clean(self) -> None:
        """
        Runs on every full_clean() call (i.e. every save through the
        repository layer). Deliberately not a field-level `validators=[...]`
        entry: Django's migration writer always imports the *django.db.models*
        module under the name `models`, which would shadow this project's
        own top-level `models` package inside the generated migration file.
        Keeping the check here avoids that name collision entirely.
        """

        Client.validate_document(self.document_number)

    @staticmethod
    def validate_document(value: str) -> None:
        """Domain rule: validates a Brazilian CPF, including its two check digits."""

        digits = re.sub(r"\D", "", value)
        if len(digits) != 11 or digits == digits[0] * 11:
            raise ValidationError({"document_number": "Invalid CPF."})

        def check_digit(partial: str) -> int:
            total = sum(
                int(digit) * weight
                for digit, weight in zip(partial, range(len(partial) + 1, 1, -1))
            )
            remainder = (total * 10) % 11
            return remainder if remainder < 10 else 0

        first_digit = check_digit(digits[:9])
        second_digit = check_digit(digits[:9] + str(first_digit))
        if digits[-2:] != f"{first_digit}{second_digit}":
            raise ValidationError({"document_number": "Invalid CPF."})

    @property
    def formatted_document(self) -> str:
        """Domain formatting: 'xxx.xxx.xxx-xx' instead of raw digits."""

        digits = self.document_number
        return f"{digits[0:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:11]}"

    def deactivate(self) -> None:
        """Domain rule: soft-disable a client instead of deleting their history."""

        self.is_active = False
