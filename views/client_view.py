"""
Terminal view for the Client resource: menus, prompts and formatted output.

All user-facing strings are in Portuguese; identifiers, comments and
docstrings follow the project's English convention.
"""

from exceptions.api_exceptions import ApiError
from utils.client.api_client import ApiClient
from utils.formatters import (
    print_error,
    print_info,
    print_section_title,
    print_success,
    print_summary_box,
    print_table,
)
from utils.prompts import prompt_choice, prompt_confirm, prompt_text
from utils.validators import is_valid_cpf, is_valid_email, is_valid_phone, parse_br_date


class ClientView:
    def __init__(self, api: ApiClient):
        self.api = api

    def menu(self) -> None:
        while True:
            print_section_title("Clientes")
            option = prompt_choice(
                "Escolha uma opção",
                [
                    ("1", "Listar clientes"),
                    ("2", "Buscar cliente por ID"),
                    ("3", "Cadastrar novo cliente"),
                    ("0", "Voltar ao menu principal"),
                ],
            )
            if option == "1":
                self._list()
            elif option == "2":
                self._show()
            elif option == "3":
                self._create()
            else:
                return

    def _list(self) -> None:
        try:
            clients = self.api.list_clients()
        except ApiError as exc:
            print_error(str(exc))
            return

        if not clients:
            print_info("Nenhum cliente cadastrado ainda. Que tal cadastrar o primeiro?")
            return

        rows = [
            (
                c["id"],
                c["name"],
                c["document_number"],
                c["phone"],
                c["email"],
                "Sim" if c["is_active"] else "Não",
            )
            for c in clients
        ]
        print_table(["ID", "Nome", "CPF", "Telefone", "E-mail", "Ativo"], rows)

    def _show(self) -> None:
        client_id = prompt_text("ID do cliente")
        try:
            client = self.api.get_client(client_id)
        except ApiError as exc:
            print_error(str(exc))
            return

        print_summary_box(
            f"Cliente #{client['id']}",
            {
                "Nome": client["name"],
                "CPF": client["document_number"],
                "Telefone": client["phone"],
                "E-mail": client["email"],
                "Nascimento": client.get("birth_date") or "não informado",
                "Ativo": "Sim" if client["is_active"] else "Não",
            },
        )

    def _create(self) -> None:
        print_section_title("Novo cliente")
        print_info(
            "Vamos coletar alguns dados. Você pode corrigir qualquer valor se algo estiver errado."
        )

        name = prompt_text("Nome completo")

        document_number = prompt_text(
            "CPF (somente números)",
            validator=lambda value: (
                None
                if is_valid_cpf(value)
                else "CPF inválido. Confira os números e tente novamente."
            ),
        )

        phone = prompt_text(
            "Telefone (com DDD)",
            validator=lambda value: (
                None
                if is_valid_phone(value)
                else "Telefone inválido. Informe DDD + número."
            ),
        )

        email = prompt_text(
            "E-mail",
            validator=lambda value: (
                None if is_valid_email(value) else "E-mail inválido."
            ),
        )

        birth_date_raw = prompt_text("Data de nascimento (dd/mm/aaaa)", optional=True)
        birth_date = parse_br_date(birth_date_raw) if birth_date_raw else None

        print_summary_box(
            "Confira os dados antes de confirmar",
            {
                "Nome": name,
                "CPF": document_number,
                "Telefone": phone,
                "E-mail": email,
                "Nascimento": birth_date or "não informado",
            },
        )

        if not prompt_confirm("Confirmar cadastro?", default=True):
            print_info("Cadastro cancelado.")
            return

        try:
            client = self.api.create_client(
                {
                    "name": name,
                    "document_number": "".join(filter(str.isdigit, document_number)),
                    "phone": phone,
                    "email": email,
                    "birth_date": birth_date,
                }
            )

        except ApiError as exc:
            print_error(f"{exc}" + (f" Detalhes: {exc.payload}" if exc.payload else ""))
            return

        print_success(
            f"Cliente '{client['name']}' cadastrado com sucesso! (ID {client['id']})"
        )

        print_info(
            "Dica: agora você já pode marcar um agendamento para este cliente no menu de Agendamentos."
        )
