from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
router = DefaultRouter()
router.register(r"consent", views.ConsentViewSet, basename="consent")
router.register(r"requests", views.DataRequestViewSet, basename="datarequest")
urlpatterns = [
    path("export/", views.export_my_data, name="export_my_data"),
    path("", include(router.urls)),
]
