from django.urls import path
from .views import (
    PlaceTypeListCreateView,
    PlaceTypeDetailView,
    TravelModeListCreateView,
    TravelModeDetailView,
    PlaceListCreateView,
    PlaceDetailView,
)

urlpatterns = [
    path("place-types/", PlaceTypeListCreateView.as_view(), name="place-type-list-create"),
    path("place-types/<int:pk>/", PlaceTypeDetailView.as_view(), name="place-type-detail"),
    path("travel-modes/", TravelModeListCreateView.as_view(), name="travel-mode-list-create"),
    path("travel-modes/<int:pk>/", TravelModeDetailView.as_view(), name="travel-mode-detail"),
    path("places/", PlaceListCreateView.as_view(), name="place-list-create"),
    path("places/<int:pk>/", PlaceDetailView.as_view(), name="place-detail"),
]