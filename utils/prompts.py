"""
Reusable terminal input helpers: prompt-and-validate loops, confirmations
and menu choices, shared by every view. Centralizing this avoids each view
re-implementing its own retry/validation logic, and is what makes the CLI
"talk back" to the user on bad input instead of just crashing or bailing.
"""

from collections.abc import Callable, Sequence

from .formatters import Color, print_error


def prompt_text(
    label: str,
    *,
    optional: bool = False,
    validator: Callable[[str], str | None] | None = None,
) -> str:
    """
    Prompts for a text value, re-asking until it passes `validator`.
    `validator` receives the raw string and returns a Portuguese error
    message if invalid, or None if valid.
    """

    while True:
        raw_value = input(f"{Color.BOLD}{label}:{Color.RESET} ").strip()

        if not raw_value and optional:
            return raw_value

        if not raw_value:
            print_error("Este campo é obrigatório.")
            continue

        if validator:
            error_message = validator(raw_value)

            if error_message:
                print_error(error_message)
                continue

        return raw_value


def prompt_int(label: str, *, minimum: int | None = None) -> int:
    while True:
        raw_value = input(f"{Color.BOLD}{label}:{Color.RESET} ").strip()

        try:
            value = int(raw_value)

        except ValueError:
            print_error("Digite um número inteiro válido.")
            continue

        if minimum is not None and value < minimum:
            print_error(f"O valor deve ser maior ou igual a {minimum}.")
            continue

        return value


def prompt_float(label: str, *, minimum: float | None = None) -> float:
    while True:
        raw_value = (
            input(f"{Color.BOLD}{label}:{Color.RESET} ").strip().replace(",", ".")
        )
        try:
            value = float(raw_value)
        except ValueError:
            print_error("Digite um valor numérico válido (ex: 45.00).")
            continue
        if minimum is not None and value < minimum:
            print_error(f"O valor deve ser maior que {minimum}.")
            continue
        return value


def prompt_confirm(label: str, *, default: bool = False) -> bool:
    hint = "S/n" if default else "s/N"

    raw_value = input(f"{Color.BOLD}{label} [{hint}]:{Color.RESET} ").strip().lower()

    if not raw_value:
        return default

    return raw_value in ("s", "sim", "y", "yes")


def prompt_choice(label: str, options: Sequence[tuple[str, str]]) -> str:
    """Displays a numbered menu built from (key, description) pairs and
    returns the chosen key, re-asking until a valid option is picked."""

    for key, description in options:
        print(f"  {Color.BOLD}{key}{Color.RESET} - {description}")

    valid_keys = {key for key, _ in options}

    while True:
        choice = input(f"{label}: ").strip()

        if choice in valid_keys:
            return choice

        print_error("Opção inválida, tente novamente.")
