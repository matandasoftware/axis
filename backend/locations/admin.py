from django.contrib import admin
from .models import LocationSample


@admin.register(LocationSample)
class LocationSampleAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "recorded_at",
        "latitude",
        "longitude",
        "accuracy_m",
        "speed_mps",
        "source",
        "device_id",
        "created_at",
    )
    list_filter = ("source", "created_at")
    search_fields = ("device_id", "user__username", "user__email")
    ordering = ("-recorded_at",)