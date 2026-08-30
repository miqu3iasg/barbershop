"""
HTTP-facing serializers for Appointment.

Business validation (working hours, conflicts, past dates) is intentionally
*not* duplicated here, it is performed by Appointment.schedule() in the
domain layer and surfaced as a DomainError, which config/exception_handler.py
translates into a 400 response.
"""

from decimal import Decimal

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from models.models import Appointment, Barber, Client, Service

from .service_serializer import ServiceSerializer


class AppointmentItemSerializer(serializers.Serializer):
    service = ServiceSerializer(read_only=True)
    quantity = serializers.IntegerField(read_only=True)
    unit_price = serializers.DecimalField(
        max_digits=8, decimal_places=2, read_only=True
    )
    duration_minutes = serializers.IntegerField(read_only=True)


class AppointmentSerializer(serializers.ModelSerializer):
    """Read-only representation of a scheduled appointment."""

    items = AppointmentItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    total_duration_minutes = serializers.SerializerMethodField()
    client_name = serializers.CharField(source="client.name", read_only=True)
    barber_name = serializers.CharField(source="barber.name", read_only=True)

    class Meta:
        model = Appointment
        fields = [  # noqa: RUF012
            "id",
            "client",
            "client_name",
            "barber",
            "barber_name",
            "start_at",
            "end_at",
            "status",
            "notes",
            "items",
            "total_price",
            "total_duration_minutes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    @extend_schema_field(serializers.DecimalField(max_digits=8, decimal_places=2))
    def get_total_price(self, obj) -> Decimal:
        return obj.total_price()

    @extend_schema_field(serializers.IntegerField())
    def get_total_duration_minutes(self, obj) -> int:
        return obj.total_duration_minutes()


class AppointmentCreateSerializer(serializers.Serializer):
    """Write-only input shape for scheduling a new appointment."""

    client_id = serializers.PrimaryKeyRelatedField(
        queryset=Client.objects.filter(is_active=True), source="client"
    )
    barber_id = serializers.PrimaryKeyRelatedField(
        queryset=Barber.objects.filter(is_active=True), source="barber"
    )
    start_at = serializers.DateTimeField()
    service_ids = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.all(), many=True, source="services", write_only=True
    )
    notes = serializers.CharField(required=False, allow_blank=True, default="")

    def create(self, validated_data):
        from services.appointment_service import AppointmentService

        services = validated_data.pop("services")
        return AppointmentService().schedule_appointment(
            client_id=validated_data["client"].id,
            barber_id=validated_data["barber"].id,
            start_at=validated_data["start_at"],
            service_ids=[service.id for service in services],
            notes=validated_data.get("notes", ""),
        )

    def to_representation(self, instance):
        return AppointmentSerializer(instance, context=self.context).data
