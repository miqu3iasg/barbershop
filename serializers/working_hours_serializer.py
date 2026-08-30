"""HTTP-facing serializer for a Barber's WorkingHours."""

from rest_framework import serializers

from models.models import WorkingHours


class WorkingHoursSerializer(serializers.ModelSerializer):
    week_day_display = serializers.CharField(
        source="get_week_day_display", read_only=True
    )

    class Meta:
        model = WorkingHours
        fields = ["id", "week_day", "week_day_display", "start_time", "end_time"]

    def validate(self, attrs):
        if attrs["start_time"] >= attrs["end_time"]:
            raise serializers.ValidationError("start_time must be before end_time.")

        return attrs
