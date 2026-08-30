"""Terminal entry-point view: welcome banner and top-level navigation."""

from utils.formatters import (
    print_banner,
    print_info,
    print_section_title,
    print_success,
)
from utils.prompts import prompt_choice


class MainMenu:
    def __init__(
        self, http_client, client_view, barber_view, service_view, appointment_view
    ):
        self.http_client = http_client
        self.client_view = client_view
        self.barber_view = barber_view
        self.service_view = service_view
        self.appointment_view = appointment_view

    def start(self) -> None:
        print_banner("Sistema de Gestão de Barbearia")
        print_info(
            "Use os números para navegar. A qualquer momento você pode voltar com a opção 0."
        )

        while True:
            print_section_title("Menu Principal")
            dev_mode_label = "ATIVADO" if self.http_client.dev_mode else "desativado"
            option = prompt_choice(
                "Escolha uma opção",
                [
                    ("1", "Clientes"),
                    ("2", "Barbeiros"),
                    ("3", "Serviços"),
                    ("4", "Agendamentos"),
                    ("5", f"Alternar modo dev (atualmente: {dev_mode_label})"),
                    ("0", "Sair"),
                ],
            )
            if option == "1":
                self.client_view.menu()
            elif option == "2":
                self.barber_view.menu()
            elif option == "3":
                self.service_view.menu()
            elif option == "4":
                self.appointment_view.menu()
            elif option == "5":
                self.http_client.set_dev_mode(not self.http_client.dev_mode)
                state = "ativado" if self.http_client.dev_mode else "desativado"
                print_success(
                    f"Modo dev {state}. Você verá as requisições e respostas HTTP em tempo real."
                )
            else:
                print_info("Até logo! 👋")
                return
