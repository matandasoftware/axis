from datetime import date as date_type

from django.utils.dateparse import parse_date
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import DailySummary
from .serializers import DailySummarySerializer


class DailySummaryView(APIView):
    """
    GET /api/v1/intelligence/daily/<yyyy-mm-dd>/

    Returns the DailySummary for that date if it exists.
    If it doesn't exist yet, returns a "zeroed" summary (not saved).
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, day: str):
        parsed = parse_date(day)
        if parsed is None:
            return Response(
                {"detail": "Invalid date format. Use YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        summary = DailySummary.objects.filter(user=request.user, date=parsed).first()

        if summary is None:
            # Return an unsaved placeholder so the UI always gets a consistent shape.
            summary = DailySummary(
                user=request.user,
                date=parsed,
                tasks_created=0,
                tasks_completed=0,
                tasks_cancelled=0,
                minutes_estimated=0,
                minutes_actual=0,
                extra=None,
            )

        data = DailySummarySerializer(summary).data
        return Response(data, status=status.HTTP_200_OK)