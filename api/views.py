from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, mixins

from api.models import Guide, Version
from api.paginator import CustomPagination
from api.serializers import (ElementSerializer, GuideSerializer,
                             SearchDateSerializer, VersionSerializer)
from api.usecases import Glossary


RESPONSE_MESSAGES = {
    'no_pointed_version_in_guide': 'Guide has not pointed version',
    'no_code_or_value_in_request': 'No code/value in parameters',
    'validation_success_text': 'element is valid',
    'validation_fail_text': 'no such element'
}


class ListRetrieveViewSet(mixins.ListModelMixin,
                          mixins.RetrieveModelMixin,
                          GenericViewSet):

    def _validate_element_in_version(self, glossary: Glossary) -> Response:
        version = glossary.get_version_for_validation_or_none()
        if version is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if glossary.is_element_valid():
            return Response(RESPONSE_MESSAGES['validation_success_text'],
                            status=status.HTTP_200_OK)

        return Response(RESPONSE_MESSAGES['validation_fail_text'],
                        status=status.HTTP_404_NOT_FOUND)


class GuideViewSet(ListRetrieveViewSet):
    serializer_class = GuideSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = Version.objects.actual_versions()
        input_date = self.request.query_params.get('search_date')

        if input_date is not None:
            serializer = SearchDateSerializer(
                data={'search_date': input_date}
            )
            serializer.is_valid(raise_exception=True)
            search_date = serializer.validated_data.get('search_date', None)

            if search_date is not None:
                queryset = Version.objects.actual_versions(date=search_date)

        return queryset

    def retrieve(self, request, *args, **kwargs):
        """Returns guide with actual version and it's elements."""

        guide_id = self.kwargs.get('pk')
        glossary = Glossary(guide_id=guide_id)
        guide = glossary.get_guide_object_or_none()  # django shortcut is not applicable since we show Version object to user.

        if guide is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        guide_actual_version = guide.get_actual_version()

        if guide_actual_version is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        elements = guide_actual_version.elements.all()

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
    def validate_elements_in_actual_version(self, request, *args, **kwargs):
        """Validates element in guide with actual version"""

        code = request.query_params.get('code')
        value = request.query_params.get('value')

        if (code is None) or (value is None):
            return Response(RESPONSE_MESSAGES['no_code_or_value_in_request'],
                            status=status.HTTP_400_BAD_REQUEST)

        glossary = Glossary(
            guide_id=kwargs.get('guide_id'),
            element_data={'code': code, 'value': value}
        )
        response = self._validate_element_in_version(glossary=glossary)

        return response


class VersionViewSet(ListRetrieveViewSet):
    serializer_class = VersionSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        guide_id = self.kwargs.get('guide_id')
        guide = get_object_or_404(Guide, pk=guide_id)
        return guide.versions.valid_versions()

    def retrieve(self, request, *args, **kwargs):
        """Returns guide elements of pointed version."""
        guide_id = kwargs.get('guide_id')
        guide = get_object_or_404(Guide, pk=guide_id)
        glossary = Glossary(
            guide_id=guide_id,
            version_id=kwargs.get('pk')
        )

        if not glossary.is_glossary_version_valid_for_guide():
            return Response(status=status.HTTP_404_NOT_FOUND)

        version = glossary.get_version_object_by_id_or_none()
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
        """Validates element in guide with actual version"""

        code = request.query_params.get('code')
        value = request.query_params.get('value')

        if (code is None) or (value is None):
            return Response(RESPONSE_MESSAGES['no_code_or_value_in_request'],
                            status=status.HTTP_400_BAD_REQUEST)

        glossary = Glossary(
            guide_id=kwargs.get('guide_id'),
            version_id=kwargs.get('pk'),
            element_data={'code': code, 'value': value}
        )
        response = self._validate_element_in_version(glossary=glossary)

        return response
