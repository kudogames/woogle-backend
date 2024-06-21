import json
from datetime import datetime
import os
import logging
from rest_framework import status
from django.utils.text import slugify
from django.utils.decorators import method_decorator
from rest_framework.decorators import action, APIView
from django.conf import settings
from rest_framework_extensions.cache.decorators import cache_response
from settings import LOG_DIR
from rest_framework.response import Response
from utils.response import APIResponse
from utils.viewsets import ModelViewSet
from utils.pagination import APIPageNumberPagination

from article import models as article_models
from article import serializers as article_serializers
from system import filters as system_filters
from system import decorators as system_decorators
from system import serializers as system_serializers


@method_decorator(system_decorators.api_auth, name='dispatch')
class ArticleDataViewSet(ModelViewSet):
    queryset = article_models.Article.objects.all()
    serializer_class = system_serializers.ArticleDataSerializer
    filterset_class = system_filters.ArticleDataFilter
    pagination_class = APIPageNumberPagination
    ordering_fields = ('rank', 'create_time', 'update_time')

    @action(methods=['post'], detail=False)
    def batch_add(self, request):
        data = request.data.get('data')

        create_success_uid_list = []
        create_error_uid_list = []

        for article_info in data:
            try:
                tags = article_info.pop('tags', [])
                categories = article_info.pop('categories', [])

                article_obj = article_models.Article.objects.update_or_create(
                    uid=article_info.get('uid'),
                    defaults={
                        'update_time': datetime.now(),
                        'title': article_info.get('title', ''),
                        'slug':article_info.get('slug', ''),
                        'description': article_info.get('description', ''),
                        'content': article_info.get('content', ''),
                        'cover_img': article_info.get('cover_img', ''),
                        'referrer_ad_creative': article_info.get('referrer_ad_creative', ''),

                    }
                )[0]

                article_obj.tags.clear()
                for tag in tags:
                    tag_name = tag.get('name')
                    tag_obj = article_models.Tag.objects.get_or_create(
                        name=tag_name,
                        defaults={
                            'name': tag_name
                        }
                    )[0]
                    article_obj.tags.add(tag_obj)

                article_obj.categories.clear()
                for category in categories:
                    category_name = category.get('name')
                    category_obj = article_models.Category.objects.get_or_create(
                        name=category_name,
                        defaults={
                            'name': category_name
                        }
                    )[0]
                    article_obj.categories.add(category_obj)
                article_obj.save()
                create_success_uid_list.append(article_info.get('uid'))
            except Exception as e:
                print(e)
                create_error_uid_list.append(article_info.get('uid'))
        data = {
            'create_success_uid_list': create_success_uid_list,
            'create_error_uid_list': create_error_uid_list
        }

        return APIResponse(data=data, status=status.HTTP_200_OK, msg='success')

    @action(methods=['post'], detail=False)
    def update_category_rank(self, request):
        data = request.data.get('data')

        category_name = data.get('category_name', '')
        rank = data.get('rank', [])

        slug = slugify(category_name)
        article_models.CategoryGroupRank.objects.update_or_create(
            slug=slug,
            defaults={
                'rank': rank
            }
        )

        return APIResponse(status=status.HTTP_200_OK, msg='success')


@method_decorator(system_decorators.api_auth, name='dispatch')
class SearchAdInfoDataViewSet(ModelViewSet):
    queryset = article_models.SearchAdInfo.objects.all()
    serializer_class = system_serializers.ArticleDataSearchAdInfoSerializer

    @action(methods=['post'], detail=False)
    def batch_add(self, request):
        data = request.data
        create_success_uid_list = []
        create_error_uid_list = []
        for ad_info in data:
            try:
                article_models.SearchAdInfo.objects.create(**ad_info)
                create_success_uid_list.append(ad_info.get('uid'))
            except Exception as e:
                create_error_uid_list.append(ad_info.get('uid'))
        data = {
            'create_success_uid_list': create_success_uid_list,
            'create_error_uid_list': create_error_uid_list,
        }

        return APIResponse(data=data, status=status.HTTP_200_OK, msg='success')


class GetWoogleSheetDataView(APIView):

    def post(self, request):
        data = request.data
        article_list = article_models.Article.objects.filter(uid__in=data)
        article_list_data = system_serializers.WoogleSheetDataSerializer(article_list, many=True).data
        return APIResponse(data=article_list_data, status=status.HTTP_200_OK)


class SitemapPageView(APIView):
    def cache_key(self, view_instance, view_method, request, args, kwargs):
        return f'backend:seniorassist:sitemap'

    @cache_response(timeout=settings.CACHE_TIME_SITEMAP, key_func='cache_key')
    def get(self, request):
        article_objs = article_models.Article.objects.all()

        sitemap = [
            {
                'url': '/',
                'changefreq': 'weekly',
                'priority': 1,
                'lastmod': datetime.now()
            },
            {
                'url': '/q',
                'changefreq': 'weekly',
                'priority': 1,
                'lastmod': datetime.now()
            },
            {
                'url': '/c/vehicle-donation',
                'changefreq': 'weekly',
                'priority': 0.9,
                'lastmod': datetime.now()
            },
            {
                'url': '/c/vehicle-plans',
                'changefreq': 'weekly',
                'priority': 0.9,
                'lastmod': datetime.now()
            },
            {
                'url': '/c/motor-vehicles',
                'changefreq': 'weekly',
                'priority': 0.9,
                'lastmod': datetime.now()
            },
            {
                'url': '/c/repair',
                'changefreq': 'weekly',
                'priority': 0.9,
                'lastmod': datetime.now()
            },

        ]

        article_sitemap_data = article_serializers.ArticleSitemapSerializer(
            instance=article_objs, many=True, context={'route': 'article'}).data

        sitemap = sitemap + article_sitemap_data

        return Response(sitemap)
