from rest_framework import serializers

from  utils.shortcuts import short_uuid

from article import models as article_models


class ArticleDataSearchAdInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = article_models.SearchAdInfo
        fields = ('uid', 'terms', 'channel_id')


class WoogleSheetDataSerializer(serializers.ModelSerializer):
    uuid = serializers.SerializerMethodField()

    def get_uuid(self,obj):
        return short_uuid()

    class Meta:
        model = article_models.Article
        fields = ('uid', 'uuid', 'slug')


class ArticleDataTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = article_models.Tag
        fields = ('name',)


class ArticleDataCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = article_models.Category
        fields = ('name',)


class ArticleDataSerializer(serializers.ModelSerializer):
    tags = ArticleDataTagSerializer(many=True)
    categories = ArticleDataCategorySerializer(many=True)

    class Meta:
        model = article_models.Article
        fields = (
            'create_time', 'update_time', 'uid', 'title', 'slug', 'description', 'content', 'cover_img', 'rank', 'tags',
            'categories')
