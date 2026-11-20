from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
router = DefaultRouter()
# Added basename='teachingartifact' to fix the router assertion error
router.register(r'artifacts', views.TeachingArtifactViewSet, basename='teachingartifact')
urlpatterns = [
    path('', include(router.urls)),
]
