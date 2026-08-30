"""
Thin wrapper around `requests`, responsible for all HTTP communication with
the Django backend. Centralizes timeout, headers, and error translation so
the presentation layer (views/) never touches `requests` directly.

`requests` was chosen over shelling out to `curl` because it gives native
error/timeout handling, connection reuse and automatic JSON handling in
plain Python, instead of parsing another process's stdout.
"""

import json

import requests

from config.cli_settings import API_BASE_URL, REQUEST_TIMEOUT
from exceptions.api_exceptions import (
    ApiConnectionError,
    ApiError,
    ResourceNotFoundError,
    ValidationApiError,
)
from utils.formatters import Color


class HttpClient:
    def __init__(self, base_url: str = API_BASE_URL, dev_mode: bool = False):
        self.base_url = base_url.rstrip("/")
        self.dev_mode = dev_mode
        self.session = requests.Session()
        self.session.headers.update(
            {"Content-Type": "application/json", "Accept": "application/json"}
        )

    def set_dev_mode(self, enabled: bool) -> None:
        self.dev_mode = enabled

    def _build_url(self, path: str) -> str:
        return f"{self.base_url}/{path.lstrip('/')}"

    def _log_request(self, method, url, params, body) -> None:
        if not self.dev_mode:
            return

        print(f"\n{Color.DIM}┌── [MODO DEV] Requisição HTTP ────────────────────────")
        print(f"│ {method} {url}")

        if params:
            print(f"│ Query params: {params}")

        if body is not None:
            print("│ Corpo:")

            for line in json.dumps(
                body, indent=2, ensure_ascii=False, default=str
            ).splitlines():
                print(f"│   {line}")

        print(
            f"└───────────────────────────────────────────────────────{Color.RESET}\n"
        )

    def _log_response(self, response) -> None:
        if not self.dev_mode:
            return

        print(f"{Color.DIM}┌── [MODO DEV] Resposta HTTP ───────────────────────────")
        print(f"│ Status: {response.status_code}")

        try:
            body = json.dumps(
                response.json(), indent=2, ensure_ascii=False, default=str
            )

        except ValueError:
            body = response.text

        for line in body.splitlines():
            print(f"│   {line}")

        print(
            f"└───────────────────────────────────────────────────────{Color.RESET}\n"
        )

    def _perform(self, method, path, params=None, json_body=None):
        url = self._build_url(path)
        self._log_request(method, url, params, json_body)

        try:
            response = self.session.request(
                method, url, params=params, json=json_body, timeout=REQUEST_TIMEOUT
            )

        except requests.exceptions.ConnectionError as exc:
            raise ApiConnectionError(
                "Não foi possível conectar à API. Ela está rodando? (python manage.py runserver)"
            ) from exc

        except requests.exceptions.Timeout as exc:
            raise ApiConnectionError(
                "A API demorou demais para responder (timeout)."
            ) from exc

        self._log_response(response)
        return self._handle_response(response)

    @staticmethod
    def _handle_response(response):
        if response.status_code == 204:
            return None

        try:
            data = response.json() if response.content else None
        except ValueError:
            data = None

        if response.status_code == 404:
            raise ResourceNotFoundError(
                "Recurso não encontrado.", response.status_code, data
            )

        if response.status_code == 400:
            raise ValidationApiError("Dados inválidos.", response.status_code, data)

        if response.status_code >= 500:
            raise ApiError("Erro interno da API.", response.status_code, data)

        if response.status_code >= 400:
            raise ApiError("Erro ao comunicar com a API.", response.status_code, data)

        return data

    def get(self, path, params=None):
        return self._perform("GET", path, params=params)

    def post(self, path, json_body=None):
        return self._perform("POST", path, json_body=json_body)

    def patch(self, path, json_body=None):
        return self._perform("PATCH", path, json_body=json_body)

    def delete(self, path):
        return self._perform("DELETE", path)
