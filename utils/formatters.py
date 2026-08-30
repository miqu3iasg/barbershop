"""
Terminal presentation helpers: banners, tables, colored feedback messages.

This module is the system's "view" toolkit, every string it prints is in
Portuguese, since that's what the end user sees, while the code itself
(names, comments, docstrings) follows the project's English convention.
"""


class Color:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"


def print_banner(text: str) -> None:
    """Prints a prominent boxed banner, used for the app's welcome title."""
    width = max(60, len(text) + 4)
    border = "═" * width
    print(f"\n{Color.CYAN}{Color.BOLD}╔{border}╗")
    print(f"║{text.center(width)}║")
    print(f"╚{border}╝{Color.RESET}")


def print_section_title(text: str) -> None:
    width = max(48, len(text) + 4)
    filler = "─" * max(0, width - len(text) - 4)
    print(f"\n{Color.BLUE}{Color.BOLD}── {text} {filler}{Color.RESET}")


def print_step(current: int, total: int, description: str) -> None:
    print(f"{Color.MAGENTA}[Passo {current}/{total}]{Color.RESET} {description}")


def print_info(message: str) -> None:
    print(f"{Color.CYAN}ℹ {message}{Color.RESET}")


def print_success(message: str) -> None:
    print(f"\n{Color.GREEN}✓ {message}{Color.RESET}\n")


def print_warning(message: str) -> None:
    print(f"\n{Color.YELLOW}⚠ {message}{Color.RESET}\n")


def print_error(message: str) -> None:
    print(f"\n{Color.RED}✗ Erro: {message}{Color.RESET}\n")


def print_table(headers, rows) -> None:
    if not rows:
        print(f"{Color.DIM}(nenhum registro encontrado){Color.RESET}")
        return

    widths = [len(str(header)) for header in headers]
    for row in rows:
        for index, value in enumerate(row):
            widths[index] = max(widths[index], len(str(value)))

    def format_row(values):
        return " │ ".join(
            str(value).ljust(widths[index]) for index, value in enumerate(values)
        )

    print(f"{Color.BOLD}{format_row(headers)}{Color.RESET}")
    print("─┼─".join("─" * width for width in widths))
    for row in rows:
        print(format_row(row))


def print_summary_box(title: str, fields: dict) -> None:
    """Prints a labeled key/value summary, used for 'confirm before submitting' screens."""

    print_section_title(title)
    label_width = max(len(label) for label in fields) + 1
    for label, value in fields.items():
        print(f"  {Color.DIM}{(label + ':').ljust(label_width)}{Color.RESET} {value}")
