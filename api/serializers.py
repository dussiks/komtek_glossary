from api.models import Element, Guide, Version
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer


class GuideSerializer(ModelSerializer):

    class Meta:
        model = Guide
        fields = ('id', 'title', 'slug', 'description')


class Version(ModelSerializer):

    class Meta:
        model = Version
        fields = ('id', 'name', 'start_date')


class ElementSerializer(ModelSerializer):
    version_id = serializers.SlugRelatedField(
        slug_field='version.id',
        many=False,
        read_only=True
    )

    class Meta:
        model = Element
        fields = ('id', 'version_id', 'code', 'value')
