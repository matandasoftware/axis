from django.conf import settings
from django.db import models


class TaskCategory(models.Model):
    """User-owned categories for organizing tasks (e.g. Work, Personal, Health)."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="task_categories",
    )
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default="#007AFF")  # Hex like "#RRGGBB"
    icon = models.CharField(max_length=50, blank=True, null=True)  # Optional UI icon key/name

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "task_categories"
        verbose_name_plural = "Task Categories"
        unique_together = ["user", "name"]  # Prevent duplicates per user
        ordering = ["name"]
        indexes = [
            models.Index(fields=["user", "name"]),
        ]

    def __str__(self) -> str:
        return f"{self.user.username} - {self.name}"


class Task(models.Model):
    """
    Core task model.

    Datetimes should be timezone-aware (Django typically stores UTC) and displayed in the user's timezone.
    - due_date: a deadline datetime (can be date-only in UI, but stored as datetime)
    - scheduled_time: planned start datetime for agenda/smart scheduling
    """

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        URGENT = "urgent", "Urgent"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        IN_PROGRESS = "in_progress", "In Progress"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tasks",
    )
    category = models.ForeignKey(
        TaskCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
    )

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    # Scheduling (optional)
    due_date = models.DateTimeField(blank=True, null=True)  # Deadline datetime
    scheduled_time = models.DateTimeField(blank=True, null=True)  # Planned start datetime
    estimated_duration = models.IntegerField(
        help_text="Planned duration in minutes",
        blank=True,
        null=True,
    )

    # Optional location link (location-based tasks)
    # String reference prevents import cycles; requires locations.Place to exist.
    location = models.ForeignKey(
        "locations.Place",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
    )

    # Completion
    completed_at = models.DateTimeField(blank=True, null=True)
    actual_duration = models.IntegerField(
        help_text="Actual duration in minutes",
        blank=True,
        null=True,
    )

    # Recurrence
    is_recurring = models.BooleanField(default=False)
    recurrence_pattern = models.JSONField(
        blank=True,
        null=True,
        help_text='Only used when is_recurring=true. Example: {"type":"daily","interval":1}',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "tasks"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["user", "due_date"]),
            models.Index(fields=["user", "scheduled_time"]),
        ]

    def __str__(self) -> str:
        return self.title


class TaskCompletion(models.Model):
    """
    Completion event log (primarily for recurring tasks).

    Keep one Task row; each time it’s completed, add a TaskCompletion record.
    This allows recurring tasks to be "completed" multiple times over time.
    """

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="completions")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="task_completions",
    )

    completed_at = models.DateTimeField()
    actual_duration = models.IntegerField(help_text="Duration in minutes", blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "task_completions"
        ordering = ["-completed_at"]
        indexes = [
            models.Index(fields=["user", "completed_at"]),
            models.Index(fields=["task", "completed_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.task.title} - {self.completed_at}"