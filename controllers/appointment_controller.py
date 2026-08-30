"""HTTP controller for the Appointment resource, the scheduling use-case."""

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from repositories.appointment_repository import AppointmentRepository
from serializers.appointment_serializer import (
    AppointmentCreateSerializer,
    AppointmentSerializer,
)
from services.appointment_service import AppointmentService


@extend_schema_view(
    list=extend_schema(
        summary="List appointments",
        description="Supports filtering by status, barber and client.",
    ),
    retrieve=extend_schema(summary="Retrieve an appointment"),
    create=extend_schema(
        summary="Schedule a new appointment",
        description=(
            "Receives client, barber, start time and the list of desired services. "
            "Duration, end time and total price are computed automatically, and the "
            "barber's availability is validated against existing appointments and working hours."
        ),
        request=AppointmentCreateSerializer,
        responses=AppointmentSerializer,
    ),
)
class AppointmentViewSet(viewsets.ModelViewSet):
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["status", "barber", "client"]
    http_method_names = ["get", "post", "head", "options"]

    def get_queryset(self):
        return AppointmentRepository().get_queryset()

    def get_serializer_class(self):
        return (
            AppointmentCreateSerializer
            if self.action == "create"
            else AppointmentSerializer
        )

    @extend_schema(summary="Cancel an appointment")
    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        appointment = AppointmentService().cancel_appointment(pk)
        return Response(AppointmentSerializer(appointment).data)

    @extend_schema(summary="Confirm an appointment")
    @action(detail=True, methods=["post"])
    def confirm(self, request, pk=None):
        appointment = AppointmentService().confirm_appointment(pk)
        return Response(AppointmentSerializer(appointment).data)
