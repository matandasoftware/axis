from django.db.models import Q
from django.utils.dateparse import parse_datetime
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import PlaceType, TravelMode, Place, LocationSample
from .serializers import (
    PlaceTypeSerializer,
    TravelModeSerializer,
    PlaceSerializer,
    LocationSampleSerializer,
    LocationSampleIngestSerializer,
)


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


class LocationSampleIngestView(APIView):
    """
    POST /api/v1/locations/samples/

    Body:
    { "samples": [ {recorded_at, latitude, longitude, ...}, ... ] }

    Notes:
    - Attaches request.user server-side (client cannot spoof user)
    - Uses bulk_create for speed
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        ingest = LocationSampleIngestSerializer(data=request.data)
        ingest.is_valid(raise_exception=True)

        samples_data = ingest.validated_data["samples"]

        objs = [
            LocationSample(user=request.user, **item)
            for item in samples_data
        ]

        LocationSample.objects.bulk_create(objs, batch_size=500)

        return Response(
            {"inserted": len(objs)},
            status=status.HTTP_201_CREATED,
        )


class LocationSampleListView(generics.ListAPIView):
    """
    GET /api/v1/locations/samples/?from=<iso>&to=<iso>

    Debug/listing endpoint (keep it for development; you can restrict later).
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = LocationSampleSerializer

    def get_queryset(self):
        qs = LocationSample.objects.filter(user=self.request.user).order_by("-recorded_at")

        from_raw = self.request.query_params.get("from")
        to_raw = self.request.query_params.get("to")

        if from_raw:
            from_dt = parse_datetime(from_raw)
            if from_dt is not None:
                qs = qs.filter(recorded_at__gte=from_dt)

        if to_raw:
            to_dt = parse_datetime(to_raw)
            if to_dt is not None:
                qs = qs.filter(recorded_at__lte=to_dt)

        return qs