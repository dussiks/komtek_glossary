import datetime as dt

from api.models import Element, Guide, Version
from api.serializers import (ElementSerializer, GuideSerializer,
                             SearchDateSerializer, VersionSerializer)
from django.db.models import OuterRef, Subquery
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import mixins, GenericViewSet

from api.paginator import CustomPagination
from api.utils import get_object_or_none


class ListRetrieveViewSet(mixins.ListModelMixin,
                          mixins.RetrieveModelMixin,
                          GenericViewSet):
    pagination_class = CustomPagination

    def _get_actual_date(self, **kwargs) -> dt.date:
        """Returns date from request params if given or today date if not."""
        input_date = self.request.query_params.get('search_date')
        current_date = dt.date.today()

        if input_date is not None:
            serializer = SearchDateSerializer(
                data={'search_date': input_date}
            )
            serializer.is_valid(raise_exception=True)
            search_date = serializer.validated_data.get('search_date', None)

            if search_date is not None:
                current_date = search_date

        return current_date

    def get_validated_element_response(self, request, version: Version):
        """
        Validates if element in guide's version.
        :param request: checks code and value parameters in request
        :param version: guide's version.
        :return: Response object with validation result
        """
        code = request.query_params.get('code')
        value = request.query_params.get('value')

        if (not code) or (not value):
            error_text = 'No code/value in parameters.'
            return Response(error_text, status=status.HTTP_400_BAD_REQUEST)

        code, value = code.lower(), value.lower()

        try:
            element = version.elements.get(code=code, value=value)
        except Element.DoesNotExist:
            fail_text = 'No such element'
            return Response(fail_text, status=status.HTTP_404_NOT_FOUND)

        success_text = 'Element validated'
        return Response(success_text, status=status.HTTP_200_OK)


class GuideViewSet(ListRetrieveViewSet):
    serializer_class = GuideSerializer
    queryset = Version.objects.all()

    def list(self, request, *args, **kwargs):
        """
        Returns guides with actual versions.
        If 'search_date' parameter is given in request - returns guides
        with versions actual to given date.
        """
        actual_date = self._get_actual_date(**kwargs)
        queryset = self.get_queryset()
        all_actual_versions = queryset.filter(start_date__lte=actual_date)
        sq = all_actual_versions.filter(
            guide_id=OuterRef('guide_id')
        ).order_by(
            '-start_date'
        )  # subquery for the final queryset
        guide_actual_versions = Version.objects.filter(
            pk=Subquery(sq.values('pk')[:1])
        )

        page = self.paginate_queryset(guide_actual_versions)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(guide_actual_versions, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """
        Returns guide having id pointed in request with actual version
        and list of referred elements.
        """
        guide = get_object_or_none(Guide, pk=kwargs.get('pk'))
        if not guide:
            return Response(status=status.HTTP_404_NOT_FOUND)

        actual_version = guide.show_actual_version
        if not actual_version:
            return Response(status=status.HTTP_404_NOT_FOUND)

        elements = actual_version.elements.all()

        page = self.paginate_queryset(elements)
        if page is not None:
            serializer = ElementSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ElementSerializer(elements, many=True)
        return Response(serializer.data)

    @action(methods=['GET'], detail=True, url_path=r'validate',
            url_name='validate_element')
    def validate_elements_in_actual_version(self, request, *args, **kwargs):
        """Validates element in guide with actual version"""
        guide = get_object_or_none(Guide, pk=kwargs.get('pk'))
        if not guide:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        actual_version = guide.show_actual_version
        if not actual_version:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        response = self.get_validated_element_response(request,
                                                       version=actual_version)
        return response


class VersionViewSet(ListRetrieveViewSet):
    serializer_class = VersionSerializer

    def get_queryset(self):
        current_date = dt.date.today()
        guide = get_object_or_none(Guide, pk=self.kwargs.get('guide_id'))
        if not guide:
            return Guide.objects.none()

        queryset = guide.versions.filter(start_date__lte=current_date)
        return queryset

    def list(self, request, *args, **kwargs):
        """Returns queryset of all versions for pointed guide."""
        guide_versions = self.get_queryset()
        if not guide_versions:  # no versions means no requested guide
            return Response(status=status.HTTP_400_BAD_REQUEST)

        page = self.paginate_queryset(guide_versions)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(guide_versions, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """Returns guide elements of pointed version."""
        guide_versions = self.get_queryset()
        if not guide_versions:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        actual_version = get_object_or_none(Version, pk=kwargs.get('pk'))
        if not actual_version:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if actual_version not in guide_versions:
            error_text = 'Guide has no such version.'
            return Response(error_text, status=status.HTTP_400_BAD_REQUEST)

        elements = actual_version.elements.all()

        page = self.paginate_queryset(elements)
        if page is not None:
            serializer = ElementSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ElementSerializer(elements, many=True)
        return Response(serializer.data)

    @action(methods=['GET'], detail=True, url_path=r'validate',
            url_name='validate_element')
    def validate_elements_in_pointed_version(self, request, *args, **kwargs):
        """Validates element in guide with pointed version"""
        guide_versions = self.get_queryset()
        if not guide_versions:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        pointed_version = get_object_or_none(Version, pk=kwargs.get('pk'))
        if not pointed_version:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if pointed_version not in guide_versions:
            error_text = 'Guide has no such version.'
            return Response(error_text, status=status.HTTP_400_BAD_REQUEST)

        response = self.get_validated_element_response(request,
                                                       version=pointed_version)
        return response
