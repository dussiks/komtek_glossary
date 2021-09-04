import datetime as dt
from typing import Optional

from api.models import Element, Guide, Version
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer


class SearchDateSerializer(serializers.Serializer):
    search_date = serializers.DateField()


class VersionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Version
        fields = ('id', 'name', 'start_date')


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

    class Meta:
        model = Element
        fields = ('id', 'code', 'value')


class GuideVersionSerializer(serializers.ModelSerializer):
    guide = serializers.CharField(source='guide.short_title')
    guide_id = serializers.IntegerField(source='guide.id')
    version = serializers.CharField(source='name')
    elements = ElementSerializer(many=True)

    class Meta:
        model = Version
        fields = ('guide', 'guide_id', 'version', 'elements')
