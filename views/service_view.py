"""Terminal view for the Service (catalog) resource."""

from exceptions.api_exceptions import ApiError
from utils.client.api_client import ApiClient
from utils.formatters import (
    print_error,
    print_info,
    print_section_title,
    print_success,
    print_table,
)
from utils.prompts import prompt_choice, prompt_float, prompt_int, prompt_text


class ServiceView:
    def __init__(self, api: ApiClient):
        self.api = api

    def menu(self) -> None:
        while True:
            print_section_title("Serviços")
            option = prompt_choice(
                "Escolha uma opção",
                [
                    ("1", "Listar serviços"),
                    ("2", "Cadastrar novo serviço"),
                    ("0", "Voltar ao menu principal"),
                ],
            )
            if option == "1":
                self._list()
            elif option == "2":
                self._create()
            else:
                return

    def _list(self) -> None:
        try:
            services = self.api.list_services()
        except ApiError as exc:
            print_error(str(exc))
            return

        if not services:
            print_info(
                "Nenhum serviço cadastrado ainda. Cadastre o primeiro para poder marcar agendamentos."
            )
            return

        rows = [
            (
                s["id"],
                s["name"],
                s["duration_minutes"],
                f"R$ {s['price']}",
                "Sim" if s["is_active"] else "Não",
            )
            for s in services
        ]
        print_table(["ID", "Nome", "Duração (min)", "Preço", "Ativo"], rows)

    def _create(self) -> None:
        print_section_title("Novo serviço")
        name = prompt_text("Nome do serviço (ex: Corte, Barba)")
        description = prompt_text("Descrição", optional=True)
        duration_minutes = prompt_int("Duração em minutos", minimum=5)
        price = prompt_float("Preço (ex: 45.00)", minimum=0.01)

        try:
            service = self.api.create_service(
                {
                    "name": name,
                    "description": description,
                    "duration_minutes": duration_minutes,
                    "price": price,
                }
            )
        except ApiError as exc:
            print_error(f"{exc}" + (f" Detalhes: {exc.payload}" if exc.payload else ""))
            return

        print_success(
            f"Serviço '{service['name']}' cadastrado com sucesso! (ID {service['id']})"
        )
