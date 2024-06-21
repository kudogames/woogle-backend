from rest_framework import serializers
from datetime import datetime

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

    tag_list = serializers.ListField(write_only=True, required=True)
    category_list = serializers.ListField(write_only=True, required=True)

    def update(self, instance, validated_data):

        instance.update_time = validated_data.get(datetime.now(), instance.update_time)
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.content = validated_data.get('content', instance.content)
        instance.cover_img = validated_data.get('cover_img', instance.cover_img)
        instance.rank = validated_data.get('rank', instance.rank)

        tag_list = validated_data.get('tag_list')
        instance.tags.clear()
        for tag in tag_list:
            tag_obj, _ = article_models.Tag.objects.get_or_create(name=tag)
            instance.tags.add(tag_obj)

        category_list = validated_data.get('category_list')
        instance.categories.clear()
        for category in category_list:
            category_obj, _ = article_models.Category.objects.get_or_create(name=category)
            instance.categories.add(category_obj)

        instance.save()
        return instance

    class Meta:
        model = article_models.Article
        fields = (
            'create_time', 'update_time', 'uid', 'title', 'slug', 'description', 'content', 'cover_img', 'rank', 'tags',
            'categories', 'tag_list', 'category_list')
