"""
URL configuration for the legislative app.

Defines API endpoints and web interface routes for legislator and bill data access.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    BillViewSet,
    LegislatorViewSet,
    bill_detail_view,
    bills_view,
    home_view,
    legislator_detail_view,
    legislators_view,
    stats_api_view,
)

router = DefaultRouter()
router.register(r"legislators", LegislatorViewSet, basename="legislator")
router.register(r"bills", BillViewSet, basename="bill")

urlpatterns = [
    # Web interface routes
    path("", home_view, name="home"),
    path("legislators/", legislators_view, name="legislators"),
    path(
        "legislators/<int:legislator_id>/",
        legislator_detail_view,
        name="legislator_detail",
    ),
    path("bills/", bills_view, name="bills"),
    path("bills/<int:bill_id>/", bill_detail_view, name="bill_detail"),
    # API routes
    path("api/stats/", stats_api_view, name="stats_api"),
    path("api/", include(router.urls)),
]
