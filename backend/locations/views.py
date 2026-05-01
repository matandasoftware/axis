from django.db.models import Q
from django.utils.dateparse import parse_datetime
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.conf import settings
from django.core.cache import cache
from django.db import transaction
import urllib.parse
import urllib.request
import json

from .models import PlaceType, TravelMode, Place, LocationSample, VisitCandidate, VisitSegment
from .serializers import (
    PlaceTypeSerializer,
    TravelModeSerializer,
    PlaceSerializer,
    LocationSampleSerializer,
    LocationSampleIngestSerializer,
    VisitCandidateSerializer,
    VisitCandidateAcceptSerializer,
    InlinePlaceCreateSerializer,
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
    throttle_scope = "location_ingest"

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
    throttle_scope = "default"

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

class VisitCandidateListView(generics.ListAPIView):
    """
    GET /api/v1/locations/visit-candidates/?status=pending&from=<iso>&to=<iso>
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = VisitCandidateSerializer
    throttle_scope = "default"

    def get_queryset(self):
        qs = VisitCandidate.objects.filter(user=self.request.user).order_by("-arrived_at")

        status_raw = self.request.query_params.get("status")
        if status_raw:
            qs = qs.filter(status=status_raw)

        from_raw = self.request.query_params.get("from")
        to_raw = self.request.query_params.get("to")

        if from_raw:
            from_dt = parse_datetime(from_raw)
            if from_dt is not None:
                qs = qs.filter(arrived_at__gte=from_dt)

        if to_raw:
            to_dt = parse_datetime(to_raw)
            if to_dt is not None:
                qs = qs.filter(arrived_at__lte=to_dt)

        return qs


class VisitCandidateRejectView(APIView):
    """
    POST /api/v1/locations/visit-candidates/<id>/reject/
    """
    permission_classes = [permissions.IsAuthenticated]
    throttle_scope = "default"

    def post(self, request, pk: int):
        c = VisitCandidate.objects.filter(user=request.user, pk=pk).first()
        if not c:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        c.status = VisitCandidate.STATUS_REJECTED
        c.save(update_fields=["status"])
        return Response({"status": c.status}, status=status.HTTP_200_OK)


class VisitCandidateAcceptView(APIView):
    """
    POST /api/v1/locations/visit-candidates/<id>/accept/

    Body:
      - { "place_id": 123 }
      OR
      - { "place": { "name", "latitude", "longitude", "radius_m?", "address?" } }

    Creates (or links) a VisitSegment, and marks candidate accepted.
    """
    permission_classes = [permissions.IsAuthenticated]
    throttle_scope = "default"

    @transaction.atomic
    def post(self, request, pk: int):
        c = VisitCandidate.objects.select_for_update().filter(user=request.user, pk=pk).first()
        if not c:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        if c.status != VisitCandidate.STATUS_PENDING:
            return Response({"detail": f"Candidate is {c.status}."}, status=status.HTTP_400_BAD_REQUEST)

        ser = VisitCandidateAcceptSerializer(data=request.data)
        ser.is_valid(raise_exception=True)

        place = None
        if ser.validated_data.get("place_id"):
            place = Place.objects.filter(user=request.user, id=ser.validated_data["place_id"]).first()
            if not place:
                return Response({"detail": "Invalid place_id."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            place_data = ser.validated_data["place"]
            # enforce uniqueness user+name like your model
            name = place_data["name"].strip()
            if Place.objects.filter(user=request.user, name=name).exists():
                return Response({"detail": "You already have a place with this name."}, status=status.HTTP_400_BAD_REQUEST)

            place = Place.objects.create(
                user=request.user,
                name=name,
                address=place_data.get("address"),
                latitude=place_data["latitude"],
                longitude=place_data["longitude"],
                radius_m=place_data.get("radius_m"),
            )

        # Link to an existing overlapping VisitSegment if it exists, else create a new one
        overlap = VisitSegment.objects.filter(
            user=request.user,
            place=place,
            arrived_at__lte=c.departed_at or c.arrived_at,
        ).filter(
            Q(departed_at__isnull=True) | Q(departed_at__gte=c.arrived_at)
        ).order_by("-arrived_at").first()

        if overlap:
            vs = overlap
        else:
            vs = VisitSegment.objects.create(
                user=request.user,
                place=place,
                arrived_at=c.arrived_at,
                departed_at=c.departed_at,
                inferred=True,   # you requested inferred_true
                confidence=None,
            )

        c.status = VisitCandidate.STATUS_ACCEPTED
        c.place = place
        c.visit_segment = vs
        c.save(update_fields=["status", "place", "visit_segment"])

        return Response(
            {
                "candidate": VisitCandidateSerializer(c).data,
                "visit_segment_id": vs.id,
                "place_id": place.id,
            },
            status=status.HTTP_200_OK,
        )


class PlaceSearchView(APIView):
    """
    GET /api/v1/locations/place-search/?q=<text>&country=ZA&limit=5&include_saved=1

    - Saved places are optionally included first (include_saved=1)
    - Primary geocoder: Nominatim (free)
    """
    permission_classes = [permissions.IsAuthenticated]
    throttle_scope = "place_search"

    def get(self, request):
        q = (request.query_params.get("q") or "").strip()
        if not q:
            return Response({"results": []}, status=status.HTTP_200_OK)

        limit = int(request.query_params.get("limit") or 5)
        limit = max(1, min(limit, 20))

        include_saved_raw = (request.query_params.get("include_saved") or "1").strip().lower()
        include_saved = include_saved_raw not in ("0", "false", "no", "off")

        country = (request.query_params.get("country") or getattr(settings, "DEFAULT_PLACE_SEARCH_COUNTRY", "ZA")).strip().upper()

        results = []

        # 1) Saved places first (optional)
        if include_saved:
            saved = (
                Place.objects.filter(user=request.user, name__icontains=q)
                .order_by("name")[:limit]
            )
            for p in saved:
                results.append(
                    {
                        "type": "saved_place",
                        "id": p.id,
                        "label": p.name,
                        "address": p.address,
                        "latitude": str(p.latitude) if p.latitude is not None else None,
                        "longitude": str(p.longitude) if p.longitude is not None else None,
                        "provider": "axis",
                        "raw": None,
                    }
                )

        # 2) External suggestions (Nominatim)
        remaining = max(0, limit - len(results))
        if remaining == 0:
            return Response({"results": results}, status=status.HTTP_200_OK)

        cache_key = f"nominatim:search:{country}:{q}:{remaining}"
        cached = cache.get(cache_key)
        if cached is not None:
            results.extend(cached)
            return Response({"results": results}, status=status.HTTP_200_OK)

        nominatim_results = []
        try:
            params = {
                "q": q,
                "format": "jsonv2",
                "limit": str(remaining),
                "addressdetails": "1",
            }
            if country:
                params["countrycodes"] = country.lower()

            url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(params)

            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": getattr(settings, "NOMINATIM_USER_AGENT", "axis-core/1.0"),
                    "Accept": "application/json",
                },
                method="GET",
            )

            with urllib.request.urlopen(req, timeout=8) as resp:
                data = json.loads(resp.read().decode("utf-8"))

            for item in data:
                nominatim_results.append(
                    {
                        "type": "geocode",
                        "label": item.get("display_name"),
                        "address": item.get("display_name"),
                        "latitude": item.get("lat"),
                        "longitude": item.get("lon"),
                        "provider": "nominatim",
                        "raw": item,
                    }
                )

        except Exception as e:
            print("Nominatim error:", repr(e))
            nominatim_results = []

        cache.set(cache_key, nominatim_results, timeout=60 * 60 * 24)
        results.extend(nominatim_results)

        return Response({"results": results}, status=status.HTTP_200_OK)