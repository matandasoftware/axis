from django.conf import settings
from django.db import models


class DailySummary(models.Model):
    """
    One row per user per calendar date.

    Purpose:
    - Store derived/cached daily metrics (task completion, time totals, etc.)
    - Avoid recomputing expensive aggregates on every API request
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="daily_summaries",
    )

    # Store as a date (not datetime) to represent a user's "day bucket".
    date = models.DateField(db_index=True)

    # Task metrics (start minimal; expand later)
    tasks_created = models.PositiveIntegerField(default=0)
    tasks_completed = models.PositiveIntegerField(default=0)
    tasks_cancelled = models.PositiveIntegerField(default=0)

    minutes_estimated = models.PositiveIntegerField(default=0)
    minutes_actual = models.PositiveIntegerField(default=0)

    # Optional: a place to store extra computed signals without schema churn
    extra = models.JSONField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "daily_summaries"
        ordering = ["-date"]
        constraints = [
            models.UniqueConstraint(fields=["user", "date"], name="uniq_daily_summary_user_date")
        ]
        indexes = [
            models.Index(fields=["user", "date"]),
        ]

    def __str__(self) -> str:
        return f"{self.user_id} summary {self.date}"

class PatternRule(models.Model):
    """
    User-defined rule that can influence scheduling/insights.

    Keep it generic and schema-light early:
    - kind: what type of rule it is (e.g. "time_preference", "avoid_location")
    - config: JSON payload for rule parameters
    - is_active: can disable without deleting
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="pattern_rules",
    )

    name = models.CharField(max_length=120)
    kind = models.CharField(max_length=50)
    config = models.JSONField(default=dict, blank=True)

    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=0, help_text="Higher applies first when conflicts occur.")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "pattern_rules"
        ordering = ["-priority", "name"]
        indexes = [
            models.Index(fields=["user", "kind"]),
            models.Index(fields=["user", "is_active"]),
        ]
        constraints = [
            models.UniqueConstraint(fields=["user", "name"], name="uniq_pattern_rule_user_name")
        ]

    def __str__(self) -> str:
        return f"{self.user_id} - {self.name}"