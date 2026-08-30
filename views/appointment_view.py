"""Terminal view for the Appointment scheduling flow, the richest wizard in the CLI."""

from exceptions.api_exceptions import ApiError
from utils.client.api_client import ApiClient
from utils.formatters import (
    print_error,
    print_info,
    print_section_title,
    print_step,
    print_success,
    print_summary_box,
    print_table,
    print_warning,
)
from utils.prompts import prompt_choice, prompt_confirm, prompt_text
from utils.validators import parse_br_datetime


class AppointmentView:
    def __init__(self, api: ApiClient):
        self.api = api

    def menu(self) -> None:
        while True:
            print_section_title("Agendamentos")
            option = prompt_choice(
                "Escolha uma opção",
                [
                    ("1", "Listar agendamentos"),
                    ("2", "Marcar novo agendamento"),
                    ("3", "Cancelar agendamento"),
                    ("4", "Confirmar agendamento"),
                    ("0", "Voltar ao menu principal"),
                ],
            )
            if option == "1":
                self._list()
            elif option == "2":
                self._create()
            elif option == "3":
                self._cancel()
            elif option == "4":
                self._confirm()
            else:
                return

    def _list(self) -> None:
        try:
            appointments = self.api.list_appointments()

        except ApiError as exc:
            print_error(str(exc))
            return

        if not appointments:
            print_info("Nenhum agendamento encontrado.")
            return

        rows = [
            (
                a["id"],
                a["client_name"],
                a["barber_name"],
                a["start_at"],
                a["status"],
                f"R$ {a['total_price']}",
            )
            for a in appointments
        ]

        print_table(["ID", "Cliente", "Barbeiro", "Início", "Status", "Valor"], rows)

    def _create(self) -> None:
        print_section_title("Novo agendamento")
        print_info("Vou te guiar em 4 passos: cliente, barbeiro, serviços e horário.")

        try:
            clients = self.api.list_clients(is_active=True)
            barbers = self.api.list_barbers(is_active=True)
            services = self.api.list_services(is_active=True)
        except ApiError as exc:
            print_error(str(exc))
            return

        if not clients:
            print_warning(
                "Não há clientes ativos cadastrados. Cadastre um cliente antes de agendar."
            )
            return

        if not barbers:
            print_warning(
                "Não há barbeiros ativos cadastrados. Cadastre um barbeiro antes de agendar."
            )
            return

        if not services:
            print_warning(
                "Não há serviços ativos cadastrados. Cadastre um serviço antes de agendar."
            )
            return

        print_step(1, 4, "Selecione o cliente")
        print_table(["ID", "Nome"], [(c["id"], c["name"]) for c in clients])
        client_id = prompt_text("ID do cliente")

        print_step(2, 4, "Selecione o barbeiro")
        print_table(["ID", "Nome"], [(b["id"], b["name"]) for b in barbers])
        barber_id = prompt_text("ID do barbeiro")

        print_step(3, 4, "Selecione os serviços desejados")
        print_table(
            ["ID", "Serviço", "Duração (min)", "Preço"],
            [
                (s["id"], s["name"], s["duration_minutes"], f"R$ {s['price']}")
                for s in services
            ],
        )

        service_ids_raw = prompt_text("IDs dos serviços (separados por vírgula)")
        try:
            service_ids = [
                int(value) for value in service_ids_raw.split(",") if value.strip()
            ]
        except ValueError:
            print_error("IDs de serviço inválidos.")
            return

        print_step(4, 4, "Escolha a data e o horário")
        start_at_raw = prompt_text("Data e hora de início (dd/mm/aaaa HH:MM)")
        notes = prompt_text("Observações", optional=True)

        try:
            start_at = parse_br_datetime(start_at_raw)
        except ValueError:
            print_error("Data/hora inválida. Use o formato dd/mm/aaaa HH:MM.")
            return

        selected_client = next(
            (c for c in clients if str(c["id"]) == str(client_id)), None
        )

        selected_barber = next(
            (b for b in barbers if str(b["id"]) == str(barber_id)), None
        )

        selected_services = [s for s in services if s["id"] in service_ids]

        print_summary_box(
            "Confira o agendamento antes de confirmar",
            {
                "Cliente": selected_client["name"]
                if selected_client
                else f"ID {client_id}",
                "Barbeiro": selected_barber["name"]
                if selected_barber
                else f"ID {barber_id}",
                "Serviços": ", ".join(s["name"] for s in selected_services)
                or "(nenhum selecionado)",
                "Início": start_at_raw,
                "Observações": notes or "nenhuma",
            },
        )

        if not prompt_confirm("Confirmar agendamento?", default=True):
            print_info("Agendamento cancelado.")
            return

        try:
            appointment = self.api.create_appointment(
                {
                    "client_id": int(client_id),
                    "barber_id": int(barber_id),
                    "start_at": start_at,
                    "service_ids": service_ids,
                    "notes": notes,
                }
            )
        except ApiError as exc:
            print_error(f"{exc}" + (f" Detalhes: {exc.payload}" if exc.payload else ""))
            return

        print_success(
            f"Agendamento #{appointment['id']} confirmado para {appointment['start_at']}! "
            f"Duração total: {appointment['total_duration_minutes']} min. "
            f"Valor total: R$ {appointment['total_price']}."
        )

    def _cancel(self) -> None:
        appointment_id = prompt_text("ID do agendamento a cancelar")
        if not prompt_confirm(
            "Tem certeza que deseja cancelar este agendamento?", default=False
        ):
            print_info("Operação cancelada.")
            return

        try:
            self.api.cancel_appointment(appointment_id)
        except ApiError as exc:
            print_error(str(exc))
            return

        print_success("Agendamento cancelado com sucesso.")

    def _confirm(self) -> None:
        appointment_id = prompt_text("ID do agendamento a confirmar")
        try:
            self.api.confirm_appointment(appointment_id)
        except ApiError as exc:
            print_error(str(exc))
            return

        print_success("Agendamento confirmado com sucesso.")
