import datetime as dt
from typing import Optional

from django.contrib import admin

from api.models import Element, Guide, Version


class VersionInline(admin.TabularInline):
    model = Version


class GuideAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'short_title',
        'description',
        'show_actual_version_name',
        'show_actual_version_date'
    )
    list_filter = ('title',)
    empty_value_display = '-пусто-'
    inlines = (VersionInline,)
    actions = ['show_actual_version_name', 'show_actual_version_date']

    def show_actual_version_date(self, obj: Guide) -> Optional[dt.date]:
        try:
            version_date = obj.show_actual_version.start_date
            return version_date
        except AttributeError:
            return

    def show_actual_version_name(self, obj: Guide) -> Optional[str]:
        try:
            version_name = obj.show_actual_version.name
            return version_name
        except AttributeError:
            return

    show_actual_version_name.short_description = 'версия'
    show_actual_version_date.short_description = 'дата начала версии'


class VersionAdmin(admin.ModelAdmin):
    list_display = ('name', 'guide', 'start_date')
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class ElementAdmin(admin.ModelAdmin):
    list_display = ('code', 'value', 'version')
    list_filter = ('code', )
    empty_value_display = '-пусто-'


admin.site.register(Element, ElementAdmin)
admin.site.register(Guide, GuideAdmin)
admin.site.register(Version, VersionAdmin)
