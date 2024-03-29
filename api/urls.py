from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api import views


router_v1 = DefaultRouter()
router_v1.register('guides', views.GuideViewSet, basename='guides')
router_v1.register(
    r'guides/(?P<guide_id>\d+)/versions',
    views.VersionViewSet,
    basename='versions',
)

urlpatterns = [
    path('v1/', include(router_v1.urls)),
]
