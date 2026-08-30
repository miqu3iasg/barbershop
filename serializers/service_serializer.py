"""HTTP-facing serializer for the Service (catalog) resource."""

from rest_framework import serializers

from models.models import Service


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = [
            "id",
            "name",
            "description",
            "duration_minutes",
            "price",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
