from django.urls import path
from .views import (
    TaskCategoryListCreateView,
    TaskCategoryDetailView,
    TaskListCreateView,
    TaskDetailView,
)

urlpatterns = [
    path("categories/", TaskCategoryListCreateView.as_view(), name="task-category-list-create"),
    path("categories/<int:pk>/", TaskCategoryDetailView.as_view(), name="task-category-detail"),
    path("", TaskListCreateView.as_view(), name="task-list-create"),
    path("<int:pk>/", TaskDetailView.as_view(), name="task-detail"),
]