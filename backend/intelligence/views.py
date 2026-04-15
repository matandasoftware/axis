from django.db.models import Sum
from django.utils.dateparse import parse_date
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from tasks.models import Task
from .models import DailySummary, PatternRule
from .serializers import DailySummarySerializer, PatternRuleSerializer


class DailySummaryView(APIView):
    """
    GET /api/v1/intelligence/daily/<yyyy-mm-dd>/?bucket=scheduled|due

    - bucket=scheduled (default): minutes_estimated sums tasks whose scheduled_time falls on that date.
    - bucket=due: minutes_estimated sums tasks whose due_date falls on that date.

    We persist the summary row so future reads are fast and Week 7 (Celery) can precompute it.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, day: str):
        parsed = parse_date(day)
        if parsed is None:
            return Response(
                {"detail": "Invalid date format. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        bucket = (request.query_params.get("bucket") or "scheduled").strip().lower()
        if bucket not in ("scheduled", "due"):
            return Response(
                {"detail": "Invalid bucket. Use 'scheduled' or 'due'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Base query: only the requesting user's tasks
        qs = Task.objects.filter(user=request.user)

        # 1) Created counts: tasks created on that calendar date
        tasks_created = qs.filter(created_at__date=parsed).count()

        # 2) Completed counts: tasks completed on that date (uses completed_at timestamp)
        tasks_completed = qs.filter(
            status=Task.Status.COMPLETED,
            completed_at__date=parsed,
        ).count()

        # 3) Cancelled counts:
        # If you have a dedicated cancelled_at later, switch to cancelled_at__date.
        tasks_cancelled = qs.filter(
            status=Task.Status.CANCELLED,
            updated_at__date=parsed,
        ).count()

        # 4) Minutes actual: sum of actual_duration for tasks completed on that date
        minutes_actual = (
            qs.filter(status=Task.Status.COMPLETED, completed_at__date=parsed)
            .aggregate(total=Sum("actual_duration"))
            .get("total")
            or 0
        )

        # 5) Minutes estimated depends on bucket rule
        if bucket == "scheduled":
            estimated_qs = qs.filter(scheduled_time__date=parsed)
        else:  # bucket == "due"
            # due_date is DateTimeField, so matching by date is safer than equality.
            estimated_qs = qs.filter(due_date__date=parsed)

        minutes_estimated = estimated_qs.aggregate(total=Sum("estimated_duration")).get("total") or 0

        # Persist one summary per user/date/bucket in extra (so you can compare later)
        summary, _created = DailySummary.objects.get_or_create(
            user=request.user,
            date=parsed,
            defaults={"extra": {}},
        )

        # Store both results in extra so switching bucket doesn't "destroy" the other.
        extra = summary.extra or {}
        extra["bucket"] = bucket
        extra.setdefault("computed", {})
        extra["computed"][bucket] = {
            "minutes_estimated": int(minutes_estimated),
            "tasks_created": int(tasks_created),
            "tasks_completed": int(tasks_completed),
            "tasks_cancelled": int(tasks_cancelled),
            "minutes_actual": int(minutes_actual),
        }
        summary.extra = extra

        # Primary fields reflect the currently requested bucket (so the response is simple)
        summary.tasks_created = tasks_created
        summary.tasks_completed = tasks_completed
        summary.tasks_cancelled = tasks_cancelled
        summary.minutes_estimated = minutes_estimated
        summary.minutes_actual = minutes_actual

        summary.save(
            update_fields=[
                "tasks_created",
                "tasks_completed",
                "tasks_cancelled",
                "minutes_estimated",
                "minutes_actual",
                "extra",
                "updated_at",
            ]
        )

        return Response(DailySummarySerializer(summary).data, status=status.HTTP_200_OK)

class PatternRuleListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PatternRuleSerializer

    def get_queryset(self):
        return PatternRule.objects.filter(user=self.request.user).order_by("-priority", "name")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PatternRuleDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PatternRuleSerializer

    def get_queryset(self):
        return PatternRule.objects.filter(user=self.request.user)