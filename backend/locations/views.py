from django.db.models import Q
from rest_framework import generics, permissions

from .models import PlaceType, TravelMode, Place
from .serializers import PlaceTypeSerializer, TravelModeSerializer, PlaceSerializer


class PlaceTypeListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PlaceTypeSerializer

    def get_queryset(self):
        return PlaceType.objects.filter(Q(user__isnull=True) | Q(user=self.request.user)).order_by("name")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PlaceTypeDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PlaceTypeSerializer

    def get_queryset(self):
        # Only user-owned types are editable/deletable
        return PlaceType.objects.filter(user=self.request.user)


class TravelModeListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TravelModeSerializer

    def get_queryset(self):
        return TravelMode.objects.filter(Q(user__isnull=True) | Q(user=self.request.user)).order_by("name")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TravelModeDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TravelModeSerializer

    def get_queryset(self):
        # Only user-owned modes are editable/deletable
        return TravelMode.objects.filter(user=self.request.user)


class PlaceListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PlaceSerializer

    def get_queryset(self):
        return Place.objects.filter(user=self.request.user).select_related("place_type").order_by("name")

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PlaceDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PlaceSerializer

    def get_queryset(self):
        return Place.objects.filter(user=self.request.user).select_related("place_type")

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx