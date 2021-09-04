
def get_guide_actual_version(serializer, obj: Guide) -> Optional[Version]:
    search_date = serializer.context.get('search_date')

    if search_date is not None:
        actual_version = obj.show_actual_version(search_date)
    else:
        actual_version = obj.show_actual_version()

    if actual_version is not None:
        return actual_version


class GuideSerializer(ModelSerializer):
    version = serializers.SerializerMethodField('get_version_name')
    start_date = serializers.SerializerMethodField('get_version_date')

    class Meta:
        model = Guide
        fields = ('title', 'id', 'short_title', 'version', 'start_date')

    def get_version_name(self, obj: Guide) -> Optional[str]:
        version = get_guide_actual_version(self, obj)

        if version is not None:
            return version.name

    def get_version_date(self, obj: Guide) -> Optional[dt.date]:
        version = get_guide_actual_version(self, obj)

        if version is not None:
            return version.start_date





class GuideViewSet(ListViewSet):
    serializer_class = GuideSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        input_date = self.request.query_params.get('search_date')

        if input_date is not None:
            serializer = VersionDateSerializer(data={'search_date': input_date})
            serializer.is_valid(raise_exception=True)
            search_date = serializer.validated_data.get('search_date', None)

            if search_date is not None:
                context.update({
                    'search_date': search_date,
                })
        return context

    def get_queryset(self):
        input_date = self.request.query_params.get('search_date')
        queryset = Guide.objects.all()

        if input_date is not None:
            serializer = VersionDateSerializer(data={'search_date': input_date})
            serializer.is_valid(raise_exception=True)
            search_date = serializer.validated_data.get('search_date', None)

            if search_date is not None:
                actual_versions = Version.objects.filter(start_date__lte=search_date).values('id')
                queryset = Guide.objects.filter(versions__id__in=actual_versions)
        print(queryset)
        return queryset

