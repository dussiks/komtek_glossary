import datetime as dt

from django.db import models
from django.db.models import OuterRef, Subquery


CURRENT_DATE = dt.date.today()


class VersionQuerySet(models.QuerySet):
    def get_valid_to_date_versions(self, date):
        return self.filter(start_date__lte=date)

    def get_only_actual_versions(self):
        sq = self.filter(
            guide_id=OuterRef('guide_id')
        ).order_by(
            '-start_date'
        )  # subquery for the final queryset
        actual_versions = self.filter(
            pk=Subquery(sq.values('pk')[:1])
        )
        return actual_versions


class VersionManager(models.Manager):
    def get_queryset(self):
        return VersionQuerySet(model=self.model, using=self._db)

    def valid_versions(self, date=CURRENT_DATE):
        """
        All versions with start_date not later than current date or
        given date are considered as valid.
        Output of versions with start_date in future if they are present
        in db will be blocked.
        """
        queryset = self.get_queryset()
        return queryset.get_valid_to_date_versions(date)

    def actual_versions(self, date=CURRENT_DATE):
        """
        Returns queryset consisting from valid versions to given date
        with last start_date value for each guide.
        """
        filter_date = min(CURRENT_DATE, date)
        queryset = self.get_queryset().get_valid_to_date_versions(filter_date)
        return queryset.get_only_actual_versions()
