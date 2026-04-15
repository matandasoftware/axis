from django.urls import path
from .views import DailySummaryView, PatternRuleListCreateView, PatternRuleDetailView

urlpatterns = [
    path("daily/<str:day>/", DailySummaryView.as_view(), name="daily-summary"),
    path("rules/", PatternRuleListCreateView.as_view(), name="pattern-rule-list-create"),
    path("rules/<int:pk>/", PatternRuleDetailView.as_view(), name="pattern-rule-detail"),
]