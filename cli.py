"""
Entry point for the terminal client.

Run this in a separate terminal AFTER the backend is up
(`python manage.py runserver` or `docker compose up`). This process never
touches Django or the database directly, it only talks to the backend
over HTTP, exactly like any other API consumer would, using the same
layered presentation (views/) and infrastructure (utils/client/) packages
that live alongside the backend code in this one project.
"""

import sys

from config.cli_settings import DEV_MODE_DEFAULT
from utils.client.api_client import ApiClient
from utils.client.http_client import HttpClient
from views.appointment_view import AppointmentView
from views.barber_view import BarberView
from views.client_view import ClientView
from views.main_menu import MainMenu
from views.service_view import ServiceView


def main() -> None:
    http_client = HttpClient(dev_mode=DEV_MODE_DEFAULT)
    api_client = ApiClient(http_client)

    menu = MainMenu(
        http_client=http_client,
        client_view=ClientView(api_client),
        barber_view=BarberView(api_client),
        service_view=ServiceView(api_client),
        appointment_view=AppointmentView(api_client),
    )

    try:
        menu.start()
    except KeyboardInterrupt:
        print("\n\nEncerrado pelo usuário. Até logo!")
        sys.exit(0)


if __name__ == "__main__":
    main()
