from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    # Versioned API
    path("api/v1/auth/", include("accounts.urls")),
    path("api/v1/tasks/", include("tasks.urls")),
    path("api/v1/locations/", include("locations.urls")),
    path("api/v1/intelligence/", include("intelligence.urls")),

    # Optional temporary backward compatibility (remove once frontend is updated)
    path("api/auth/", include("accounts.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)