from rest_framework import serializers
from .models import TaskCategory, Task


class TaskCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskCategory
        fields = [
            "id",
            "name",
            "color",
            "icon",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_name(self, value: str) -> str:
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("Category name cannot be empty.")
        return value


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            "id",
            "category",
            "title",
            "description",
            "priority",
            "status",
            "due_date",
            "scheduled_time",
            "estimated_duration",
            "location",
            "completed_at",
            "actual_duration",
            "is_recurring",
            "recurrence_pattern",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_title(self, value: str) -> str:
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("Title cannot be empty.")
        return value

    def validate_category(self, category):
        # Prevent linking to another user's TaskCategory
        if category is None:
            return category
        request = self.context.get("request")
        if request and not request.user.is_anonymous and category.user_id != request.user.id:
            raise serializers.ValidationError("Invalid category.")
        return category

    def validate_location(self, location):
        # Prevent linking to another user's Place
        if location is None:
            return location
        request = self.context.get("request")
        if request and not request.user.is_anonymous and location.user_id != request.user.id:
            raise serializers.ValidationError("Invalid location.")
        return location

    def validate(self, attrs):
        est = attrs.get("estimated_duration")
        act = attrs.get("actual_duration")

        if est is not None and est < 0:
            raise serializers.ValidationError({"estimated_duration": "Must be >= 0 minutes."})
        if act is not None and act < 0:
            raise serializers.ValidationError({"actual_duration": "Must be >= 0 minutes."})
        return attrs