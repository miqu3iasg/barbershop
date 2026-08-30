"""Application service for Service (catalog) use-cases."""

from typing import Optional

from models.models import Service
from repositories.service_repository import ServiceRepository


class ServiceCatalogService:
    def __init__(self, repository: Optional[ServiceRepository] = None):
        self.repository = repository or ServiceRepository()

    def list_services(self, is_active: Optional[bool] = None):
        filters = {} if is_active is None else {"is_active": is_active}
        return self.repository.list(**filters)

    def register_service(self, **fields) -> Service:
        return self.repository.create(**fields)
