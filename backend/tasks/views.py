from rest_framework import generics, permissions

from .models import TaskCategory, Task
from .serializers import TaskCategorySerializer, TaskSerializer


class TaskCategoryListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/tasks/categories/
    POST /api/v1/tasks/categories/
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TaskCategorySerializer

    def get_queryset(self):
        return TaskCategory.objects.filter(user=self.request.user).order_by("name")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TaskCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET/PATCH/DELETE /api/v1/tasks/categories/<id>/
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TaskCategorySerializer

    def get_queryset(self):
        return TaskCategory.objects.filter(user=self.request.user)


class TaskListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/tasks/
    POST /api/v1/tasks/
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TaskSerializer

    def get_queryset(self):
        return (
            Task.objects.filter(user=self.request.user)
            .select_related("category", "location")
            .order_by("-created_at")
        )

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TaskDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET/PATCH/DELETE /api/v1/tasks/<id>/
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user).select_related("category", "location")

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx