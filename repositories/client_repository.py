"""Data-access layer for the Client aggregate."""

from models.models import Client

from .base_repository import BaseRepository


class ClientRepository(BaseRepository):
    model = Client

    def find_by_document(self, document_number: str):
        return self.get_queryset().filter(document_number=document_number).first()

    def create(self, **fields) -> Client:
        client = Client(**fields)
        return self.save(client)
