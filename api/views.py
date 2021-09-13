import datetime as dt

from django.db.models import OuterRef, Subquery
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, mixins

from api.models import Element, Guide, Version
from api.paginator import CustomPagination
from api.serializers import (ElementSerializer, GuideSerializer,
                             SearchDateSerializer, VersionSerializer)
from api.usecases import GlossaryClass


class ListRetrieveViewSet(mixins.ListModelMixin,
                          mixins.RetrieveModelMixin,
                          GenericViewSet):
    pass


class GuideViewSet(ListRetrieveViewSet):
    pass


class VersionViewSet(ListRetrieveViewSet):
    serializer_class = VersionSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        guide_id = self.kwargs.get('guide_id')
        glossary = GlossaryClass(guide_id=guide_id)
        guide = glossary.get_guide_object_or_none()

        if guide is not None:
            return guide.versions.valid_versions()

        return Version.objects.none()


    def list(self, request, *args, **kwargs):




    def retrieve(self, request, *args, **kwargs):
        """Returns guide elements of pointed version."""
        queryset = self.get_queryset()
        glossary = GlossaryClass(
            guide_id=kwargs.get('guide_id'),
            version_id=kwargs.get('pk')
        )
        guide = glossary.get_guide_object_or_none()

        if not guide:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        version = glossary.get_version_object_or_none()

        if not version:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if not glossary.is_version_belongs_to_guide():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        elements = version.elements.all()

        page = self.paginate_queryset(elements)
        if page is not None:
            serializer = ElementSerializer(
                page,
                many=True,
                context={'guide_id': guide_id}
            )
            return self.get_paginated_response(serializer.data)

        serializer = ElementSerializer(
            elements,
            many=True,
            context={'guide_id': guide_id}
        )
        return Response(serializer.data)

    @action(methods=['GET'], detail=True, url_path=r'validate',
            url_name='validate_element')
    def validate_elements_in_pointed_version(self, request, *args, **kwargs):
        """Validates element in guide with pointed version"""
        pass
