"""HTTP-facing serializer for the Barber resource."""

from rest_framework import serializers

from models.models import Barber, Service

from .service_serializer import ServiceSerializer
from .working_hours_serializer import WorkingHoursSerializer


class BarberSerializer(serializers.ModelSerializer):
    specialties = serializers.PrimaryKeyRelatedField(
        queryset=Service.objects.all(), many=True, required=False
    )

    specialties_detail = ServiceSerializer(
        source="specialties", many=True, read_only=True
    )

    working_hours = WorkingHoursSerializer(many=True, read_only=True)

    class Meta:
        model = Barber
        fields = [
            "id",
            "name",
            "phone",
            "email",
            "hired_at",
            "is_active",
            "specialties",
            "specialties_detail",
            "working_hours",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
