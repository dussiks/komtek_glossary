import datetime as dt

from api.models import Element, Guide, Version
from api.serializers import (ElementSerializer, GuideSerializer,
                             GuideVersionSerializer, SearchDateSerializer,
                             VersionSerializer)
from django.db.models import OuterRef, Subquery
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import mixins, GenericViewSet


class ListRetrieveViewSet(mixins.ListModelMixin,
                          mixins.RetrieveModelMixin,
                          GenericViewSet):

    def get_actual_versions_or_empty_qs(self, date: dt.date, **kwargs):
        """
        Returns queryset with versions which have start_date not later
        than date pointed.
        If guide's id given in arguments - returns queryset only for guide
        having pointed id.
        :param date: date up to which guide versions are looked for.
        :param kwargs: checking if guide's id in arguments.
        :return: queryset with versions or empty queryset.
        """
        guide_id = kwargs.get('guide_id')

        if guide_id is not None:
            guide_versions = Version.objects.filter(
                guide_id=int(guide_id), start_date__lte=date
            ).order_by(
                '-start_date'
            )
        else:
            guide_versions = Version.objects.filter(
                start_date__lte=date
            ).order_by(
                '-start_date'
            )

        if not guide_versions.exists():
            return Guide.objects.none()

        return guide_versions

    def get_actual_date(self, *args, **kwargs) -> dt.date:
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


class GuideViewSet(ListRetrieveViewSet):
    serializer_class = GuideSerializer


    def get_queryset(self):
        """
        Returns queryset of guides with actual versions.
        If 'search_date' parameter is given in request - returns guides
        with versions actual to given date.
        """
        actual_date = self.get_actual_date()
        all_actual_versions = self.get_actual_versions_or_empty_qs(
            date=actual_date
        )
        sq = all_actual_versions.filter(
            guide_id=OuterRef('guide_id')
        ).order_by(
            '-start_date'
        )  # subquery for the final queryset
        queryset = Version.objects.filter(pk=Subquery(sq.values('pk')[:1]))

        return queryset

    def retrieve(self, request, *args, **kwargs):
        """
        Returns guide having id pointed in request with actual version
        and list of referred elements.
        """
        current_date = dt.date.today()
        guide_id = self.kwargs.get('pk')

        try:
            guide_id = int(guide_id)
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        guide_actual_versions = self.get_actual_versions_or_empty_qs(
            guide_id=guide_id, date=current_date
        )

        if not guide_actual_versions:  # here and after if guide has no versions up to actual moment 404 will be shown
            return Response(status=status.HTTP_404_NOT_FOUND)

        actual_version = guide_actual_versions.first()
        serializer = GuideVersionSerializer(actual_version)

        return Response(serializer.data)

    @action(methods=['GET'], detail=True, url_path=r'validate',
            url_name='validate_element')
    def validate_elements_in_guide(self, request, *args, **kwargs):
        guide_id = self.kwargs.get('pk')

        #try:
        #    guide_id = int(guide_id)
        #except ValueError:
        #    return Response(status=status.HTTP_400_BAD_REQUEST)

        guide = get_object_or_404(Guide, pk=guide_id)
        actual_version = guide.show_actual_version

        if not actual_version:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        code = self.request.query_params.get('code')
        value = self.request.query_params.get('value')

        if (not code) or (not value):
            error_text = 'No code/value in parameters.'
            return Response(error_text, status=status.HTTP_400_BAD_REQUEST)

        try:
            element = actual_version.elements.get(code=code, value=value)
        except Element.DoesNotExist:
            fail_text = 'No such element'
            return Response(fail_text, status=status.HTTP_404_NOT_FOUND)

        success_text = 'Element validated'
        return Response(success_text, status=status.HTTP_200_OK)


class VersionViewSet(ListRetrieveViewSet):
    serializer_class = VersionSerializer

    def get_queryset(self):
        current_date = dt.date.today()
        guide = get_object_or_404(Guide, pk=self.kwargs.get('guide_id'))
        queryset = self.get_actual_versions_or_empty_qs(
            guide_id=guide.id,
            date=current_date
        )

        return queryset

    def list(self, request, *args, **kwargs):
        """Returns queryset of all versions for pointed guide."""
        queryset = self.get_queryset()

        if not queryset:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """
        Returns elements of pointed in request guide and it's pointed version.
        """
        guide_versions = self.get_queryset()

        if not guide_versions:
            return Response(status=status.HTTP_404_NOT_FOUND)

        version_id = kwargs.get('pk')
        try:
            version_id = int(version_id)
        except ValueError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        actual_version = get_object_or_404(Version, pk=version_id)

        if actual_version not in guide_versions:
            error_text = 'Pointed guide has no such version.'
            return Response(error_text, status=status.HTTP_400_BAD_REQUEST)

        elements = actual_version.elements.all()
        serializer = ElementSerializer(elements, many=True)

        return Response(serializer.data)
