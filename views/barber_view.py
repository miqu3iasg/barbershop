"""Terminal view for the Barber resource, including working-hours management."""

from exceptions.api_exceptions import ApiError
from utils.client.api_client import ApiClient
from utils.formatters import (
    print_error,
    print_info,
    print_section_title,
    print_success,
    print_table,
)
from utils.prompts import prompt_choice, prompt_confirm, prompt_text
from utils.validators import is_valid_email, is_valid_phone, parse_br_date

WEEK_DAYS = [
    ("0", "Segunda-feira"),
    ("1", "Terça-feira"),
    ("2", "Quarta-feira"),
    ("3", "Quinta-feira"),
    ("4", "Sexta-feira"),
    ("5", "Sábado"),
    ("6", "Domingo"),
]


class BarberView:
    def __init__(self, api: ApiClient):
        self.api = api

    def menu(self) -> None:
        while True:
            print_section_title("Barbeiros")
            option = prompt_choice(
                "Escolha uma opção",
                [
                    ("1", "Listar barbeiros"),
                    ("2", "Cadastrar novo barbeiro"),
                    ("3", "Definir horário de trabalho"),
                    ("0", "Voltar ao menu principal"),
                ],
            )
            if option == "1":
                self._list()
            elif option == "2":
                self._create()
            elif option == "3":
                self._set_working_hours()
            else:
                return

    def _list(self) -> None:
        try:
            barbers = self.api.list_barbers()
        except ApiError as exc:
            print_error(str(exc))
            return

        if not barbers:
            print_info("Nenhum barbeiro cadastrado ainda.")
            return

        rows = [
            (
                b["id"],
                b["name"],
                b["phone"],
                b["email"],
                "Sim" if b["is_active"] else "Não",
            )
            for b in barbers
        ]
        print_table(["ID", "Nome", "Telefone", "E-mail", "Ativo"], rows)

    def _create(self) -> None:
        print_section_title("Novo barbeiro")
        name = prompt_text("Nome completo")

        phone = prompt_text(
            "Telefone (com DDD)",
            validator=lambda v: None if is_valid_phone(v) else "Telefone inválido.",
        )

        email = prompt_text(
            "E-mail",
            validator=lambda v: None if is_valid_email(v) else "E-mail inválido.",
        )

        hired_at_raw = prompt_text("Data de contratação (dd/mm/aaaa)")
        try:
            hired_at = parse_br_date(hired_at_raw)
        except ValueError:
            print_error("Data inválida. Use o formato dd/mm/aaaa.")
            return

        try:
            barber = self.api.create_barber(
                {
                    "name": name,
                    "phone": phone,
                    "email": email,
                    "hired_at": hired_at,
                    "specialties": [],
                }
            )
        except ApiError as exc:
            print_error(f"{exc}" + (f" Detalhes: {exc.payload}" if exc.payload else ""))
            return

        print_success(
            f"Barbeiro '{barber['name']}' cadastrado com sucesso! (ID {barber['id']})"
        )

        print_info(
            "Dica: use a opção 3 para definir o horário de trabalho dele antes de marcar agendamentos."
        )

    def _set_working_hours(self) -> None:
        print_section_title("Horário de trabalho")
        barber_id = prompt_text("ID do barbeiro")
        print_table(["Código", "Dia"], WEEK_DAYS)
        week_day = prompt_choice("Dia da semana", WEEK_DAYS)
        start_time = prompt_text("Horário de início (HH:MM)")
        end_time = prompt_text("Horário de término (HH:MM)")

        if not prompt_confirm(
            f"Confirmar expediente de {start_time} às {end_time}?", default=True
        ):
            print_info("Operação cancelada.")
            return

        try:
            self.api.set_barber_working_hours(
                barber_id,
                {
                    "week_day": int(week_day),
                    "start_time": start_time,
                    "end_time": end_time,
                },
            )
        except ApiError as exc:
            print_error(f"{exc}" + (f" Detalhes: {exc.payload}" if exc.payload else ""))
            return

        print_success("Horário de trabalho definido com sucesso.")
