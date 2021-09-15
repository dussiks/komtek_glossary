from typing import Optional

from api.models import Guide, Element, Version


class Glossary:
    """
    Class created for operation with basic instances used in application and
    includes Guide object id, Version object id and incoming data for
    elements validation.
    If necessary, it could be extended for more handling with instances.
    """

    def __init__(
            self,
            guide_id,
            version_id: int = None,
            element_data: dict = {},
    ):
        self._guide_id = guide_id
        self._version_id = version_id
        self._element_data = element_data

    def _get_element_attributes(self) -> tuple:
        code = self._element_data.get('code')
        value = self._element_data.get('value')
        return code, value

    def get_guide_object_or_none(self) -> Optional[Guide]:
        """Returns guide object initialized by guide_id in Glossary class"""

        try:
            guide_id = int(self._guide_id)
        except (ValueError, TypeError):
            return

        try:
            guide = Guide.objects.get(pk=guide_id)
        except Guide.DoesNotExist:
            return

        return guide

    def get_version_object_by_id_or_none(self) -> Optional[Version]:
        """
        Returns guide's version initialized by version_id in Glossary class.
        """

        try:
            version_id = int(self._version_id)
        except ValueError:
            return

        try:
            version = Version.objects.get(pk=version_id)
        except Version.DoesNotExist:
            return

        return version

    def is_glossary_version_valid_for_guide(self) -> bool:
        """Returns if Glossary class version in guide's versions"""

        guide = self.get_guide_object_or_none()
        version = self.get_version_object_by_id_or_none()

        if (version is not None) and (guide is not None):
            guide_versions = guide.versions.valid_versions()

            if version in guide_versions:
                return True

        return False

    def get_version_for_elem_validation_or_none(self) -> Optional[Version]:
        """
        Returns guide's version applicable for validation or none.
        Firstly try by Glossary class argument.
        If no one - looks for guide's actual version.
        """

        guide = self.get_guide_object_or_none()
        if guide is None:
            return

        if self._version_id is not None:
            version = self.get_version_object_by_id_or_none()

            if (version is not None
                and self.is_glossary_version_valid_for_guide()):
                return version

            return

        guide_version = guide.get_actual_version()
        if guide_version is not None:
            return guide_version

        return

    def is_element_valid(self) -> bool:
        """Validates if element in guide's version."""

        version = self.get_version_for_elem_validation_or_none()
        if version is None:
            return False

        code, value = self._get_element_attributes()
        if (code is None) or (value is None):
            return False

        try:
            element = version.elements.get(code=code, value=value)
        except Element.DoesNotExist:
            return False

        return True
