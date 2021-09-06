from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from api.models import Element, Version


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
    guide_id = serializers.SerializerMethodField()

    class Meta:
        model = Element
        fields = ('id', 'code', 'value', 'guide_id')

    def get_guide_id(self, obj):
        guide_id = self.context.get('guide_id')
        return guide_id
