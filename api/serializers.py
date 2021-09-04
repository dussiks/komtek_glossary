import datetime as dt
from typing import Optional

from api.models import Element, Guide, Version
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer


class GuideSerializer(ModelSerializer):
    title = serializers.CharField(source='guide.title')
    id = serializers.IntegerField(source='guide.id')
    short_title = serializers.CharField(source='guide.short_title')
    description = serializers.CharField(source='guide.description')
    version = serializers.CharField(source='name')

    class Meta:
        model = Version
        fields = ('title', 'id', 'short_title',
                  'description', 'version', 'start_date')


class ElementSerializer(ModelSerializer):
    version_id = serializers.SlugRelatedField(
        slug_field='version.id',
        many=False,
        read_only=True
    )

    class Meta:
        model = Element
        fields = ('id', 'version_id', 'code', 'value')


class VersionDateSerializer(serializers.Serializer):
    search_date = serializers.DateField()
