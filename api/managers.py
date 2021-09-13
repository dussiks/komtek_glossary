import datetime as dt
from typing import Optional

from django.db import models


CURRENT_DATE = dt.date.today()


class VersionManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset()

    def valid_versions(self):
        return self.get_queryset().filter(start_date__lte=CURRENT_DATE)

    def get_guides_versions(self, guide_id: int):
        return self.get_queryset().filter(guide_id=guide_id)

