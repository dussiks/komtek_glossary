import datetime as dt

from api.models import Element, Guide, Version
from api.serializers import (ElementSerializer,
                             GuideSerializer, VersionDateSerializer)
from django.db.models import Max, Count, OuterRef, Subquery
from rest_framework.response import Response
from rest_framework.viewsets import mixins, GenericViewSet


class GuideViewSet(mixins.ListModelMixin,
                   mixins.RetrieveModelMixin,
                   GenericViewSet):
    serializer_class = GuideSerializer

    def get_queryset(self):
        input_date = self.request.query_params.get('search_date')
        actual_date = dt.date.today()

        if input_date is not None:
            serializer = VersionDateSerializer(data={'search_date': input_date})
            serializer.is_valid(raise_exception=True)
            search_date = serializer.validated_data.get('search_date', None)

            if search_date is not None:
                actual_date = search_date

        actual_versions = Version.objects.filter(start_date__lte=actual_date)
        sq = actual_versions.filter(
            guide_id=OuterRef('guide_id')
        ).order_by(
            '-start_date'
        )
        queryset = Version.objects.filter(pk=Subquery(sq.values('pk')[:1]))
        return queryset
