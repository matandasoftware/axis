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