from django.urls import path
from .views import DailySummaryView

urlpatterns = [
    path("daily/<str:day>/", DailySummaryView.as_view(), name="daily-summary"),
]