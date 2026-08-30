"""HTTP controller for the Client resource."""

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters, viewsets

from repositories.client_repository import ClientRepository
from serializers.client_serializer import ClientSerializer
from services.client_service import ClientService


@extend_schema_view(
    list=extend_schema(
        summary="List clients",
        description="Returns all registered clients, with search and filtering.",
    ),
    retrieve=extend_schema(summary="Retrieve a client"),
    create=extend_schema(summary="Register a new client"),
    update=extend_schema(summary="Fully update a client"),
    partial_update=extend_schema(summary="Partially update a client"),
    destroy=extend_schema(summary="Remove a client"),
)
class ClientViewSet(viewsets.ModelViewSet):
    serializer_class = ClientSerializer
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["is_active"]
    search_fields = ["name", "document_number", "email"]
    ordering_fields = ["name", "created_at"]

    def get_queryset(self):
        return ClientRepository().get_queryset()

    def perform_create(self, serializer):
        serializer.instance = ClientService().register_client(
            **serializer.validated_data
        )
