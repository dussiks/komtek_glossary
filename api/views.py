import datetime as dt

from api.models import Element, Guide, Version
from api.serializers import (ElementSerializer, GuideSerializer,
                             GuideVersionSerializer, SearchDateSerializer,
                             VersionSerializer)
from django.db.models import OuterRef, Subquery
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import mixins, GenericViewSet


class ListRetrieveViewSet(mixins.ListModelMixin,
                          mixins.RetrieveModelMixin,
                          GenericViewSet):
    pass


class GuideViewSet(ListRetrieveViewSet):
    serializer_class = GuideSerializer

    def get_queryset(self):
        """
        Returns queryset of guides with actual versions. If 'search_date'
        parameter is given in request - returns guides with versions actual
        to given date.
        """
        input_date = self.request.query_params.get('search_date')
        actual_date = dt.date.today()

        if input_date is not None:
            serializer = SearchDateSerializer(
                data={'search_date': input_date}
            )
            serializer.is_valid(raise_exception=True)
            search_date = serializer.validated_data.get('search_date', None)

            if search_date is not None:
                actual_date = search_date

        before_date_versions = Version.objects.filter(start_date__lte=actual_date)
        sq = before_date_versions.filter(
            guide_id=OuterRef('guide_id')
        ).order_by(
            '-start_date'
        )  # subquery for the final queryset
        queryset = Version.objects.filter(pk=Subquery(sq.values('pk')[:1]))

        return queryset

    def retrieve(self, request, pk=None):
        """
        Returns pointed in request guide actual version with
        referred elements.
        """
        current_date = dt.date.today()
        guide_versions = Version.objects.filter(
            guide_id=pk, start_date__lte=current_date
        ).order_by(
            '-start_date'
        )

        if not guide_versions.exists():  # if guide has no any versions up to actual moment 404 will be shown
            return Response(status=status.HTTP_404_NOT_FOUND)

        actual_version = guide_versions.first()
        serializer = GuideVersionSerializer(actual_version)

        return Response(serializer.data)


class VersionViewSet(ListRetrieveViewSet):
    serializer_class = VersionSerializer

    def get_queryset(self):
        current_date = dt.date.today()
        queryset = Version.objects.filter(
            guide_id=self.kwargs.get('guide_id'), start_date__lte=current_date
        ).order_by(
            '-start_date'
        )

        return queryset

    def list(self, request, *args, **kwargs):
        """Returns queryset of versions for pointed guide."""
        queryset = self.get_queryset()
        if not queryset.exists():  # if guide has no any versions up to actual moment 404 will be shown
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """
        Returns elements of pointed in request guide and it's version."""
        actual_version = guide_versions.first()
        serializer = GuideVersionSerializer(actual_version)

        return Response(serializer.data)
