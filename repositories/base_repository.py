"""
Generic base repository: a thin wrapper around a Django model's manager.

Concrete repositories only add domain-specific query/persistence methods;
they never contain business rules (those live on the models themselves).
"""
from typing import Generic, Optional, TypeVar

from django.db.models import Model, QuerySet

ModelType = TypeVar("ModelType", bound=Model)


class BaseRepository(Generic[ModelType]):
    model: type

    def get_queryset(self) -> QuerySet:
        return self.model.objects.all()

    def list(self, **filters) -> QuerySet:
        return self.get_queryset().filter(**filters)

    def get_by_id(self, pk) -> Optional[ModelType]:
        return self.get_queryset().filter(pk=pk).first()

    def save(self, instance: ModelType) -> ModelType:
        """Runs full model validation (field validators + uniqueness) before persisting."""
        instance.full_clean()
        instance.save()
        return instance

    def delete(self, instance: ModelType) -> None:
        instance.delete()
