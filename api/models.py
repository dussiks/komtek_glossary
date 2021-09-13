import datetime as dt

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.functional import cached_property

from api.managers import VersionManager


class Element(models.Model):
    code = models.CharField('код', max_length=50, db_index=True)
    value = models.CharField('значение', max_length=100)

    class Meta:
        verbose_name = 'элемент'
        verbose_name_plural = 'элементы'
        ordering = ('code',)
        constraints = [
            models.UniqueConstraint(
                fields=['code', 'value'],
                name='unique_code_value'
            )
        ]

    def __str__(self):
        return self.code


class Guide(models.Model):
    title = models.CharField('наименование', max_length=100, unique=True)
    short_title = models.CharField(
        'короткое наименование',
        unique=True,
        max_length=50
    )
    description = models.CharField(
        'описание',
        max_length=200,
        null=True,
        blank=True
    )

    class Meta:
        verbose_name = 'Справочник'
        verbose_name_plural = 'Справочники'
        ordering = ('title',)

    def __str__(self):
        return self.title

    @cached_property
    def show_actual_version(self):
        """Returns guide's version actual at date when called."""
        actual_date = dt.date.today()

        try:
            actual_version = self.versions.filter(
                start_date__lte=actual_date
            ).order_by(
                'start_date'
            ).last()
            return actual_version
        except Version.DoesNotExist:
            return


class Version(models.Model):
    guide = models.ForeignKey(
        Guide,
        on_delete=models.CASCADE,
        related_name='versions',
    )
    name = models.CharField('версия справочника', max_length=100)
    start_date = models.DateField(
        'дата начала действия',
        null=False,
        blank=False
    )
    elements = models.ManyToManyField(
        Element,
        through='ElementInVersion',
        verbose_name='элемент в версии'
    )
    objects = VersionManager()


    class Meta:
        verbose_name = 'версия'
        verbose_name_plural = 'версии'
        ordering = ('-start_date',)
        constraints = [
            models.UniqueConstraint(
                fields=['guide', 'name'],
                name='unique_guide_version'
            )
        ]

    def __str__(self):
        return f'{self.guide.short_title} версия {self.name}'


class ElementInVersion(models.Model):
    version = models.ForeignKey(
        Version,
        on_delete=models.CASCADE,
        related_name='version_elements',
        verbose_name='версия'
    )
    element = models.ForeignKey(
        Element,
        on_delete=models.CASCADE,
        verbose_name='элемент'
    )

    def validate_unique(self, exclude=None):
        elems_with_code = Element.objects.filter(code=self.element.code)
        elems_in_version = ElementInVersion.objects.filter(
            version=self.version
        ).exclude(
            id=self.id
        )

        if elems_in_version.filter(element__in=elems_with_code).exists():
            raise ValidationError(
                'You already have element with such code in this version'
            )

        elems_with_value = Element.objects.filter(value=self.element.value)
        if elems_in_version.filter(element__in=elems_with_value).exists():
            raise ValidationError(
                'You already have element with such value in this version'
            )

    def save(self, *args, **kwargs):
        self.validate_unique()
        super().save(self, *args, **kwargs)

    class Meta:
        verbose_name = 'элемент в версии справочника'
        verbose_name_plural = 'элементы в версии справочника'
