"""HTTP controller for the Barber resource, including its working-hours sub-resource."""

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from repositories.barber_repository import BarberRepository
from serializers.barber_serializer import BarberSerializer
from serializers.working_hours_serializer import WorkingHoursSerializer
from services.barber_service import BarberService


@extend_schema_view(
    list=extend_schema(summary="List barbers"),
    create=extend_schema(summary="Register a new barber"),
)
class BarberViewSet(viewsets.ModelViewSet):
    serializer_class = BarberSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["is_active"]
    search_fields = ["name", "email"]

    def get_queryset(self):
        return (
            BarberRepository()
            .get_queryset()
            .prefetch_related("specialties", "working_hours")
        )

    def perform_create(self, serializer):
        data = dict(serializer.validated_data)
        specialty_ids = [service.id for service in data.pop("specialties", [])]
        serializer.instance = BarberService().register_barber(
            specialty_ids=specialty_ids, **data
        )

    @extend_schema(
        summary="Set or update the working hours for a weekday",
        request=WorkingHoursSerializer,
    )
    @action(detail=True, methods=["post"], url_path="working-hours")
    def set_working_hours(self, request, pk=None):
        barber = self.get_object()
        serializer = WorkingHoursSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        working_hours = BarberService().set_working_hours(
            barber,
            week_day=serializer.validated_data["week_day"],
            start_time=serializer.validated_data["start_time"],
            end_time=serializer.validated_data["end_time"],
        )
        return Response(WorkingHoursSerializer(working_hours).data)
