from rest_framework import serializers
from .models import DailySummary, PatternRule  # add PatternRule import


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

class PatternRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatternRule
        fields = [
            "id",
            "name",
            "kind",
            "config",
            "is_active",
            "priority",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_name(self, value: str) -> str:
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("Name cannot be empty.")
        return value

    def validate_kind(self, value: str) -> str:
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("Kind cannot be empty.")
        return value