import datetime as dt

from django.db import models
from django.utils.functional import cached_property


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


class Element(models.Model):
    version = models.ManyToManyField(
        Version,
        related_name='elements',
        verbose_name='версии'
    )
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
