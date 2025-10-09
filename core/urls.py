"""
URL configuration for core project.

Includes API endpoints and web interface for legislative data.
"""

from django.urls import include, path

urlpatterns = [
    path("", include("legislative.urls")),
]
