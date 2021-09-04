from django.urls import include, path

from api import views
from rest_framework.routers import DefaultRouter


router_v1 = DefaultRouter()
router_v1.register('guides', views.GuideViewSet, basename='guides')

urlpatterns = [
    path('', include(router_v1.urls)),
]
