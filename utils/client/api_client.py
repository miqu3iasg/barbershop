"""
Resource-oriented facade over HttpClient: one method per backend use-case,
consumed directly by the terminal views. This is the CLI's only point of
contact with the backend, it deliberately has no business logic of its
own, only request/response shaping.
"""

from .http_client import HttpClient


class ApiClient:
    def __init__(self, http_client: HttpClient):
        self.http = http_client

    # Clients

    def list_clients(self, is_active=None):
        params = {"is_active": is_active} if is_active is not None else None
        return self._results(self.http.get("clients/", params=params))

    def get_client(self, client_id):
        return self.http.get(f"clients/{client_id}/")

    def create_client(self, payload):
        return self.http.post("clients/", json_body=payload)

    # Barbers

    def list_barbers(self, is_active=None):
        params = {"is_active": is_active} if is_active is not None else None
        return self._results(self.http.get("barbers/", params=params))

    def create_barber(self, payload):
        return self.http.post("barbers/", json_body=payload)

    def set_barber_working_hours(self, barber_id, payload):
        return self.http.post(f"barbers/{barber_id}/working-hours/", json_body=payload)

    # Services

    def list_services(self, is_active=None):
        params = {"is_active": is_active} if is_active is not None else None
        return self._results(self.http.get("services/", params=params))

    def create_service(self, payload):
        return self.http.post("services/", json_body=payload)

    # Appointments

    def list_appointments(self, status=None):
        params = {"status": status} if status else None
        return self._results(self.http.get("appointments/", params=params))

    def create_appointment(self, payload):
        return self.http.post("appointments/", json_body=payload)

    def cancel_appointment(self, appointment_id):
        return self.http.post(f"appointments/{appointment_id}/cancel/")

    def confirm_appointment(self, appointment_id):
        return self.http.post(f"appointments/{appointment_id}/confirm/")

    @staticmethod
    def _results(data):
        if isinstance(data, dict) and "results" in data:
            return data["results"]
        return data or []
