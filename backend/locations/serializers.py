from rest_framework import serializers
from .models import PlaceType, TravelMode, Place, LocationSample, VisitCandidate, VisitSegment


class PlaceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaceType
        fields = ["id", "name", "color", "icon", "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate_name(self, value: str) -> str:
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("Name cannot be empty.")
        return value


class TravelModeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TravelMode
        fields = [
            "id",
            "name",
            "color",
            "icon",
            "min_speed_mps",
            "max_speed_mps",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_name(self, value: str) -> str:
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("Name cannot be empty.")
        return value

    def validate(self, attrs):
        min_speed = attrs.get("min_speed_mps")
        max_speed = attrs.get("max_speed_mps")
        if min_speed is not None and min_speed < 0:
            raise serializers.ValidationError({"min_speed_mps": "Must be >= 0."})
        if max_speed is not None and max_speed < 0:
            raise serializers.ValidationError({"max_speed_mps": "Must be >= 0."})
        if min_speed is not None and max_speed is not None and min_speed > max_speed:
            raise serializers.ValidationError("min_speed_mps cannot be greater than max_speed_mps.")
        return attrs


class PlaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Place
        fields = [
            "id",
            "name",
            "place_type",
            "address",
            "latitude",
            "longitude",
            "radius_m",
            "is_favorite",
            "notes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_name(self, value: str) -> str:
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("Name cannot be empty.")
        return value

    def validate_place_type(self, place_type):
        # Allow system (user=None) and user's own; block other users'
        if place_type is None:
            return place_type

        request = self.context.get("request")
        if request and not request.user.is_anonymous:
            if place_type.user_id is None:
                return place_type
            if place_type.user_id != request.user.id:
                raise serializers.ValidationError("Invalid place_type.")
        return place_type

    def validate(self, attrs):
        radius = attrs.get("radius_m")
        if radius is not None and radius < 0:
            raise serializers.ValidationError({"radius_m": "Must be >= 0 meters."})
        return attrs


class LocationSampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationSample
        fields = [
            "id",
            "recorded_at",
            "latitude",
            "longitude",
            "accuracy_m",
            "altitude_m",
            "speed_mps",
            "heading_deg",
            "source",
            "device_id",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_latitude(self, value):
        if value < -90 or value > 90:
            raise serializers.ValidationError("Latitude must be between -90 and 90.")
        return value

    def validate_longitude(self, value):
        if value < -180 or value > 180:
            raise serializers.ValidationError("Longitude must be between -180 and 180.")
        return value

    def validate_accuracy_m(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("accuracy_m must be >= 0.")
        return value

    def validate_speed_mps(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("speed_mps must be >= 0.")
        return value

    def validate_heading_deg(self, value):
        if value is not None and (value < 0 or value >= 360):
            raise serializers.ValidationError("heading_deg must be in [0, 360).")
        return value


class LocationSampleIngestSerializer(serializers.Serializer):
    """
    Bulk ingest format:
    { "samples": [ {sample}, {sample}, ... ] }

    We validate each entry using LocationSampleSerializer.
    """
    samples = LocationSampleSerializer(many=True)

class VisitCandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisitCandidate
        fields = [
            "id",
            "arrived_at",
            "departed_at",
            "latitude",
            "longitude",
            "radius_m",
            "dwell_seconds",
            "status",
            "place",
            "visit_segment",
            "created_at",
        ]
        read_only_fields = fields


class InlinePlaceCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    address = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    radius_m = serializers.IntegerField(required=False, allow_null=True)

    def validate_name(self, value: str) -> str:
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("Name cannot be empty.")
        return value

    def validate_radius_m(self, value):
        if value is None:
            return value
        if value < 0:
            raise serializers.ValidationError("radius_m must be >= 0.")
        return value


class VisitCandidateAcceptSerializer(serializers.Serializer):
    place_id = serializers.IntegerField(required=False)
    place = InlinePlaceCreateSerializer(required=False)

    def validate(self, attrs):
        place_id = attrs.get("place_id")
        place = attrs.get("place")
        if not place_id and not place:
            raise serializers.ValidationError("Provide either place_id or place.")
        if place_id and place:
            raise serializers.ValidationError("Provide only one of place_id or place.")
        return attrs