"""HTTP controller for the Service (catalog) resource."""

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters, viewsets

from repositories.service_repository import ServiceRepository
from serializers.service_serializer import ServiceSerializer
from services.service_catalog_service import ServiceCatalogService


@extend_schema_view(
    list=extend_schema(summary="List services offered by the barbershop"),
    create=extend_schema(summary="Register a new service (e.g. haircut, beard trim)"),
)
class ServiceViewSet(viewsets.ModelViewSet):
    serializer_class = ServiceSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["is_active"]
    search_fields = ["name"]
    ordering_fields = ["name", "price", "duration_minutes"]

    def get_queryset(self):
        return ServiceRepository().get_queryset()

    def perform_create(self, serializer):
        serializer.instance = ServiceCatalogService().register_service(
            **serializer.validated_data
        )
