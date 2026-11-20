from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
router = DefaultRouter()
# Added basename='conversation' to fix the router assertion error
router.register(r'conversations', views.ConversationViewSet, basename='conversation')
urlpatterns = [
    path('', include(router.urls)),
]
