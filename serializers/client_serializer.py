"""
HTTP-facing serializer for Client, validates request/response *shape* only.
Business rules (e.g. CPF check-digit validation, uniqueness) live on the
Client model and are enforced via full_clean() in the repository layer,
deliberately not duplicated here.
"""

from rest_framework import serializers

from models.models import Client


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = [
            "id",
            "name",
            "document_number",
            "phone",
            "email",
            "birth_date",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_phone(self, value):
        digits = "".join(filter(str.isdigit, value))

        if len(digits) < 10 or len(digits) > 11:
            raise serializers.ValidationError(
                "Phone must contain area code + number (10 or 11 digits)."
            )

        return value
