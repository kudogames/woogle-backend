from rest_framework import serializers

from article import models as article_models


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
