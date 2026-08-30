"""
Client-side input validation helpers, used to give the user instant
feedback in the terminal before a request is even sent to the API. The
backend validates everything again independently, these are purely a
user-experience shortcut, never the source of truth.
"""

import re
from datetime import datetime


def is_valid_cpf(document_number: str) -> bool:
    digits = re.sub(r"\D", "", document_number)

    if len(digits) != 11 or digits == digits[0] * 11:
        return False

    def check_digit(partial: str) -> int:
        total = sum(
            int(digit) * weight
            for digit, weight in zip(partial, range(len(partial) + 1, 1, -1))
        )

        remainder = (total * 10) % 11

        return remainder if remainder < 10 else 0

    first_digit = check_digit(digits[:9])
    second_digit = check_digit(digits[:9] + str(first_digit))

    return digits[-2:] == f"{first_digit}{second_digit}"


def is_valid_email(email: str) -> bool:
    return re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email) is not None


def is_valid_phone(phone: str) -> bool:
    digits = re.sub(r"\D", "", phone)
    return 10 <= len(digits) <= 11


def parse_br_date(text: str) -> str:
    """Converts 'dd/mm/aaaa' into ISO format ('aaaa-mm-dd'), as expected by the API."""

    return datetime.strptime(text, "%d/%m/%Y").strftime("%Y-%m-%d")


def parse_br_datetime(text: str) -> str:
    """Converts 'dd/mm/aaaa HH:MM' into an ISO-8601 datetime string."""

    return datetime.strptime(text, "%d/%m/%Y %H:%M").isoformat()
