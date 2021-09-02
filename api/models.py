from django.db import models


class Guide(models.Model):
    title = models.CharField('наименование', max_length=100, unique=True)
    slug = models.SlugField(
        'слаг',
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
        return f'{self.guide} v.{self.name}'


class Element(models.Model):
    version = models.ForeignKey(
        Version,
        on_delete=models.CASCADE,
        related_name='elements'
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
