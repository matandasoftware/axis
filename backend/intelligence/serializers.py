from rest_framework import serializers
from .models import DailySummary


class DailySummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = DailySummary
        fields = [
            "id",
            "date",
            "tasks_created",
            "tasks_completed",
            "tasks_cancelled",
            "minutes_estimated",
            "minutes_actual",
            "extra",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields