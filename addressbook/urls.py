from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse  # Add this import

def health_check(request):
    """Simple health check endpoint"""
    return HttpResponse("OK", content_type="text/plain")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('', include('contacts.urls')),
    path('health/', health_check, name='health-check'),  # Added health check
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)  # Added static files
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)