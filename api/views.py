from api.models import Element, Guide, Version
from api.serializers import ElementSerializer, GuideSerializer
from rest_framework.response import Response
from rest_framework.viewsets import mixins, GenericViewSet


class ListViewSet(mixins.ListModelMixin, GenericViewSet):
    pass


class ElementViewSet(ListViewSet):
    queryset = Element.objects.all()
    serializer_class = ElementSerializer


class GuideViewSet(ListViewSet):
    queryset = Guide.objects.all()
    serializer_class = GuideSerializer
