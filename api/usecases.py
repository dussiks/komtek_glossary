from typing import Optional

from api.models import Guide, Element, Version
from api.managers import VersionManager


class GlossaryClass:

    def __init__(
            self,
            guide_id: int = None,
            version_id: int = None,
            code: str = None,
            value: str = None
    ):
        self._guide_id = guide_id
        self._version_id = version_id
        self._code = code
        self._value = value

    def get_guide_object_or_none(self) -> Optional[Guide]:
        try:
            guide_id = int(self._guide_id)
        except ValueError:
            return

        try:
            guide = Guide.objects.get(pk=guide_id)
        except Guide.DoesNotExist:
            return

        return guide

    def get_version_object_or_none(self) -> Optional[Version]:
        try:
            version_id = int(self._version_id)
        except ValueError:
            return

        try:
            version = Version.objects.get(pk=version_id)
        except Version.DoesNotExist:
            return

        return version

    def validate_element(self) -> bool:
        try:
            element = Element.objects.get(code=self._code, value=self._value)
        except Element.DoesNotExist:
            return

        return True

    def is_version_belongs_to_guide(self) -> bool:
        """Returns if given version in guide's versions"""
        guide = self.get_guide_object_or_none()
        version = self.get_version_object_or_none()

        if (version is not None) and (guide is not None):
            guide_versions = guide.versions.valid_versions()

            if version in guide_versions:
                return True

        return

