from datetime import datetime

from django.db import models
from django.utils.text import slugify

from utils.models import TimeBaseModel


class Article(TimeBaseModel):
    uid = models.CharField(max_length=10, primary_key=True, db_index=True)
    title = models.CharField(max_length=250, default='')
    slug = models.SlugField(max_length=250, null=True, unique=True)
    description = models.TextField(max_length=5000, default='')
    content = models.TextField(max_length=50000, default='')
    cover_img = models.CharField(max_length=200, default='')
    rank = models.PositiveIntegerField(default=99999)
    tags = models.ManyToManyField('article.Tag', related_name='articles', db_constraint=False)
    categories = models.ManyToManyField('article.Category', related_name='articles', db_constraint=False)

    class Meta:
        app_label = 'article'
        db_table = 'article_article'


class Tag(TimeBaseModel):
    id = models.BigAutoField(primary_key=True, db_index=True)
    name = models.CharField(unique=True, max_length=50)

    class Meta:
        app_label = 'article'
        db_table = 'article_tag'


class Category(TimeBaseModel):
    id = models.BigAutoField(primary_key=True, db_index=True)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kwargs)

    class Meta:
        app_label = 'article'
        db_table = 'article_category'


class CategoryGroupRank(TimeBaseModel):
    id = models.BigAutoField(primary_key=True, db_index=True)
    slug = models.SlugField(unique=True)
    rank = models.JSONField(max_length=50000, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.slug)
        return super().save(*args, **kwargs)

    class Meta:
        app_label = 'article'
        db_table = 'article_category_group_rank'


class SearchAdInfo(TimeBaseModel):
    # sai_id
    uid = models.CharField(max_length=10, primary_key=True, db_index=True)
    terms = models.CharField(max_length=1000, default='')
    channel_id = models.CharField(max_length=50, default='')

    class Meta:
        app_label = 'article'
        db_table = 'article_search_ad_info'
