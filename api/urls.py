from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import ContactViewSet

router = DefaultRouter()
router.register(r'contacts', ContactViewSet)

urlpatterns = [
    path('', include(router.urls)),
]