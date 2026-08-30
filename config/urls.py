"""URL routing for the backend HTTP API. Registers each controller's router
under /api/v1/ and exposes the OpenAPI/Swagger documentation."""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.routers import DefaultRouter

from controllers.appointment_controller import AppointmentViewSet
from controllers.barber_controller import BarberViewSet
from controllers.client_controller import ClientViewSet
from controllers.service_controller import ServiceViewSet

router = DefaultRouter()
router.register("clients", ClientViewSet, basename="client")
router.register("barbers", BarberViewSet, basename="barber")
router.register("services", ServiceViewSet, basename="service")
router.register("appointments", AppointmentViewSet, basename="appointment")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include(router.urls)),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
