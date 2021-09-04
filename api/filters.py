from django_filters import rest_framework as filters
from rest_framework import status
from rest_framework.response import Response

from api.models import Element, Guide, Version


class GuideFilter(filters.FilterSet):
    versions = filters.CharFilter(method='filter_versions')

    class Meta:
        model = Guide
        fields = ('is_favorited', 'is_in_shopping_cart', 'author', 'tags')


    def filter_tags(self, queryset, name, value):
        try:
            tags_list = self.request.query_params.getlist('tags')
        except AttributeError:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        tags = Tag.objects.filter(slug__in=tags_list).values_list('id',
                                                                  flat=True)
        if tags is not None:
            return queryset.filter(tags__id__in=tags).distinct()
        return queryset


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='contains')

    class Meta:
        model = Ingredient
        fields = ('name', )
