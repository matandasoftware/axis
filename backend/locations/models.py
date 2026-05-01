from django.db import models
from django.conf import settings


class PlaceType(models.Model):
    """
    Data-driven place type (no hard-coded choices).

    - System/default types have user=NULL (shared across all users).
    - User-created types have user set (custom per user).
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='place_types',
        null=True,
        blank=True,
    )

    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default='#007AFF')  # "#RRGGBB"
    icon = models.CharField(max_length=50, blank=True, null=True)  # UI icon key/name (optional)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'place_types'
        ordering = ['name']
        indexes = [
            models.Index(fields=['user', 'name']),
            models.Index(fields=['user', 'is_active']),
        ]

    def __str__(self) -> str:
        scope = "system" if self.user_id is None else f"user:{self.user_id}"
        return f"{self.name} ({scope})"


class TravelMode(models.Model):
    """
    Data-driven travel mode used for inference and user customization.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='travel_modes',
        null=True,
        blank=True,
    )

    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default='#34C759')
    icon = models.CharField(max_length=50, blank=True, null=True)
    min_speed_mps = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    max_speed_mps = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'travel_modes'
        ordering = ['name']
        indexes = [
            models.Index(fields=['user', 'name']),
            models.Index(fields=['user', 'is_active']),
        ]

    def __str__(self) -> str:
        scope = "system" if self.user_id is None else f"user:{self.user_id}"
        return f"{self.name} ({scope})"


class Place(models.Model):
    """
    A user-saved place (Home, Gym, Office, etc.) that can be referenced by Tasks and Visits.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='places')

    name = models.CharField(max_length=255)
    place_type = models.ForeignKey(
        PlaceType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='places',
    )

    address = models.TextField(blank=True, null=True)

    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    radius_m = models.IntegerField(
        blank=True,
        null=True,
        help_text='Optional geofence radius in meters for arrival/departure inference',
    )

    is_favorite = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'places'
        ordering = ['name']
        unique_together = ['user', 'name']
        indexes = [
            models.Index(fields=['user', 'is_favorite']),
            models.Index(fields=['user', 'name']),
        ]

    def __str__(self) -> str:
        return self.name


class LocationSample(models.Model):
    """
    Raw device location samples streamed from the phone.
    """

    SOURCE_CHOICES = [
        ('phone', 'Phone'),
        ('laptop', 'Laptop'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='location_samples')

    recorded_at = models.DateTimeField(db_index=True)

    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    accuracy_m = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)
    altitude_m = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)

    speed_mps = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        blank=True,
        null=True,
        help_text='Meters/second if available from device APIs',
    )

    heading_deg = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)

    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='phone')
    device_id = models.CharField(max_length=128, blank=True, null=True)  # optional: identify phone vs laptop

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'location_samples'
        ordering = ['-recorded_at']
        indexes = [
            models.Index(fields=['user', 'recorded_at']),
        ]

    def __str__(self) -> str:
        return f"{self.user_id} @ {self.recorded_at}"


class VisitSegment(models.Model):
    """
    Derived visit segment: "user stayed at Place from arrived_at to departed_at".
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='visit_segments')
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='visit_segments')

    arrived_at = models.DateTimeField()
    departed_at = models.DateTimeField(blank=True, null=True)

    inferred = models.BooleanField(default=True)
    confidence = models.DecimalField(max_digits=4, decimal_places=3, blank=True, null=True)  # 0.000 - 1.000

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'visit_segments'
        ordering = ['-arrived_at']
        indexes = [
            models.Index(fields=['user', 'arrived_at']),
            models.Index(fields=['place', 'arrived_at']),
        ]

    def __str__(self) -> str:
        return f"{self.user_id} visit {self.place_id} @ {self.arrived_at}"


class VisitCandidate(models.Model):
    """
    A visit-like dwell cluster that couldn't be attached to a saved Place yet.
    """

    STATUS_PENDING = "pending"
    STATUS_ACCEPTED = "accepted"
    STATUS_REJECTED = "rejected"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_ACCEPTED, "Accepted"),
        (STATUS_REJECTED, "Rejected"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="visit_candidates")

    arrived_at = models.DateTimeField()
    departed_at = models.DateTimeField(blank=True, null=True)

    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    radius_m = models.IntegerField(blank=True, null=True)
    dwell_seconds = models.IntegerField(blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)

    place = models.ForeignKey(
        Place,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="visit_candidates",
    )
    visit_segment = models.ForeignKey(
        VisitSegment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="source_candidates",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "visit_candidates"
        ordering = ["-arrived_at"]
        indexes = [
            models.Index(fields=["user", "status", "arrived_at"]),
            models.Index(fields=["user", "arrived_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.user_id} candidate @ {self.arrived_at} ({self.status})"


class TravelSegment(models.Model):
    """
    Derived travel segment: "user traveled from A to B from started_at to ended_at".
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='travel_segments')

    origin_place = models.ForeignKey(
        Place,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='travel_origin_segments',
    )
    destination_place = models.ForeignKey(
        Place,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='travel_destination_segments',
    )

    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(blank=True, null=True)

    distance_m = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    duration_seconds = models.IntegerField(blank=True, null=True)

    inferred_mode = models.ForeignKey(
        TravelMode,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inferred_travel_segments',
    )
    user_selected_mode = models.ForeignKey(
        TravelMode,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='user_selected_travel_segments',
    )
    mode_confidence = models.DecimalField(max_digits=4, decimal_places=3, blank=True, null=True)  # 0..1

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'travel_segments'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['user', 'started_at']),
        ]

    def __str__(self) -> str:
        return f"{self.user_id} travel @ {self.started_at}"