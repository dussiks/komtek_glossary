import datetime as dt

from django.db import models
from django.utils.functional import cached_property


class Guide(models.Model):
    title = models.CharField('наименование', max_length=100, unique=True)
    short_title = models.SlugField(
        'короткое наименование',
        unique=True,
        allow_unicode=True,
        max_length=30
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

    def show_actual_version(self, current_date: dt.date = None):
        """
        Returns guide's version object actual for the given date.
        If date is not given - for the date when function is called.
        """
        actual_date = dt.date.today()

        if current_date is not None:
            if isinstance(current_date, dt.date):
                actual_date = current_date

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
    start_date = models.DateField('дата начала действия')

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
    versions = models.ManyToManyField(
        Version,
        related_name='elements',
        verbose_name='версии'
    )
    code = models.CharField('код', max_length=50, unique=True, db_index=True)
    value = models.CharField('значение', max_length=200)

    class Meta:
        verbose_name = 'элемент'
        verbose_name_plural = 'элементы'
        ordering = ('code',)
        constraints = [
            models.UniqueConstraint(
                fields=['code', 'value'],
                name='unique_elements_code_value'
            )
        ]

    def __str__(self):
        return self.code
