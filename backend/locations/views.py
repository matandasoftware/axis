from django.db.models import Q
from rest_framework import generics, permissions

from .models import PlaceType, TravelMode, Place
from .serializers import PlaceTypeSerializer, TravelModeSerializer, PlaceSerializer


class PlaceTypeListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/locations/place-types/
    POST /api/v1/locations/place-types/

    - List returns system defaults (user=None) + user's own.
    - Create always creates a user-owned type.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PlaceTypeSerializer

    def get_queryset(self):
        return PlaceType.objects.filter(Q(user__isnull=True) | Q(user=self.request.user)).order_by("name")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PlaceTypeDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET/PATCH/DELETE /api/v1/locations/place-types/<id>/

    Only user-owned types are editable/deletable (system types are read-only).
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PlaceTypeSerializer

    def get_queryset(self):
        return PlaceType.objects.filter(user=self.request.user)


class TravelModeListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/locations/travel-modes/
    POST /api/v1/locations/travel-modes/

    - List returns system defaults (user=None) + user's own.
    - Create always creates a user-owned travel mode.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TravelModeSerializer

    def get_queryset(self):
        return TravelMode.objects.filter(Q(user__isnull=True) | Q(user=self.request.user)).order_by("name")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TravelModeDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET/PATCH/DELETE /api/v1/locations/travel-modes/<id>/

    Only user-owned modes are editable/deletable (system modes are read-only).
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TravelModeSerializer

    def get_queryset(self):
        return TravelMode.objects.filter(user=self.request.user)


class PlaceListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/locations/places/
    POST /api/v1/locations/places/
    """
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
    """
    GET/PATCH/DELETE /api/v1/locations/places/<id>/
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PlaceSerializer

    def get_queryset(self):
        return Place.objects.filter(user=self.request.user).select_related("place_type")

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx