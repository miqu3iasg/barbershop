"""
Application service for Client use-cases.

Resolves input into domain operations and coordinates the repository.
Business rules that belong to the Client itself (e.g. CPF validation,
deactivation) live on the model; this layer is orchestration only.
"""

from typing import Optional

from models.models import Client
from repositories.client_repository import ClientRepository


class ClientService:
    def __init__(self, repository: Optional[ClientRepository] = None):
        self.repository = repository or ClientRepository()

    def list_clients(self, is_active: Optional[bool] = None):
        filters = {} if is_active is None else {"is_active": is_active}
        return self.repository.list(**filters)

    def get_client(self, client_id) -> Optional[Client]:
        return self.repository.get_by_id(client_id)

    def register_client(self, **fields) -> Client:
        return self.repository.create(**fields)

    def deactivate_client(self, client: Client) -> Client:
        client.deactivate()
        return self.repository.save(client)
