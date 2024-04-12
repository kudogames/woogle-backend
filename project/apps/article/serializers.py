from rest_framework import serializers
from utils.imgproxy import imgproxy, ImgProxyOptions
from article import models as article_models
from datetime import datetime, timezone


class CategorySerializer(serializers.ModelSerializer):
    """
    大种类
    """

    class Meta:
        model = article_models.Category
        fields = ('id', 'name', 'slug')
        read_only_fields = ('id',)


class TagSerializer(serializers.ModelSerializer):
    """
    标签
    """

    class Meta:
        model = article_models.Tag
        fields = ('id', 'name')
        read_only_fields = ('id',)


class ArticleSerializer(serializers.ModelSerializer):
    cover_img = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField(read_only=True)
    tags = serializers.SerializerMethodField(read_only=True)

    def get_cover_img(self, obj):
        options = self.context.get('options', ImgProxyOptions.COVER_IMG)
        return imgproxy.get_img_url(obj.cover_img, options=options)

    def get_category(self, obj):
        category_obj = obj.categories.first()
        return CategorySerializer(category_obj).data

    def get_tags(self, obj):
        tag_list = obj.tags.all()
        if tag_list:
            return [tag.name for tag in tag_list]
        return []

    class Meta:
        model = article_models.Article
        fields = ("uid", "title", "description", 'tags', "category", "content", "cover_img", "rank")


class ArticleSimpleSerializer(serializers.ModelSerializer):
    cover_img = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField(read_only=True)

    def get_cover_img(self, obj):
        options = self.context.get('options', ImgProxyOptions.COVER_IMG)
        return imgproxy.get_img_url(obj.cover_img, options=options)
        # return obj.cover_img

    def get_category(self, obj):
        category_obj = obj.categories.first()
        return CategorySerializer(category_obj).data

    class Meta:
        model = article_models.Article
        fields = ("uid", "title", "category", "cover_img", "rank")


class ArticleMiddleSerializer(serializers.ModelSerializer):
    cover_img = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField(read_only=True)

    def get_cover_img(self, obj):
        return imgproxy.get_img_url(obj.cover_img)

    def get_category(self, obj):
        category_obj = obj.categories.first()
        return CategorySerializer(category_obj).data

    class Meta:
        model = article_models.Article
        fields = ("uid", "title", "description", "category", "cover_img", "rank")


class ArticleSitemapSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField(read_only=True)
    changefreq = serializers.CharField(read_only=True, default='daily')
    priority = serializers.FloatField(read_only=True, default=0.6)
    lastmod = serializers.SerializerMethodField(read_only=True)

    def get_url(self, obj):
        route = self.context.get('route')
        return f'/{route}/{obj.uid}'

    def get_lastmod(self, obj):
        return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S+00:00')

    class Meta:
        model = article_models.Article
        fields = ('url', 'changefreq', 'priority', 'lastmod')
