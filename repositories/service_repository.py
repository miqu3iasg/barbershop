"""Data-access layer for the Service (catalog) aggregate."""
from models.models import Service

from .base_repository import BaseRepository


class ServiceRepository(BaseRepository):
    model = Service

    def active(self):
        return self.list(is_active=True)

    def create(self, **fields) -> Service:
        service = Service(**fields)
        return self.save(service)
