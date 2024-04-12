import json
from datetime import datetime

from rest_framework import status
from django.utils.decorators import method_decorator
from rest_framework.decorators import action, APIView
from django.conf import settings
from rest_framework_extensions.cache.decorators import cache_response

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
                        **article_info
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
                'url': '/love',
                'changefreq': 'weekly',
                'priority': 1,
                'lastmod': datetime.now()
            }, {
                'url': '/q',
                'changefreq': 'weekly',
                'priority': 1,
                'lastmod': datetime.now()
            },
            {
                'url': '/c/health',
                'changefreq': 'weekly',
                'priority': 0.9,
                'lastmod': datetime.now()
            },
            {
                'url': '/c/career',
                'changefreq': 'weekly',
                'priority': 0.9,
                'lastmod': datetime.now()
            },
            {
                'url': '/c/education',
                'changefreq': 'weekly',
                'priority': 0.9,
                'lastmod': datetime.now()
            },
            {
                'url': '/c/housing',
                'changefreq': 'weekly',
                'priority': 0.9,
                'lastmod': datetime.now()
            },
            {
                'url': '/c/lifestyle',
                'changefreq': 'weekly',
                'priority': 0.9,
                'lastmod': datetime.now()
            },
            {
                'url': '/c/fashion',
                'changefreq': 'weekly',
                'priority': 0.9,
                'lastmod': datetime.now()
            },
            {
                'url': '/c/law',
                'changefreq': 'weekly',
                'priority': 0.9,
                'lastmod': datetime.now()
            },
            {
                'url': '/c/game',
                'changefreq': 'weekly',
                'priority': 0.9,
                'lastmod': datetime.now()
            },
            {
                'url': '/c/tv-show',
                'changefreq': 'weekly',
                'priority': 0.9,
                'lastmod': datetime.now()
            },
            {
                'url': '/c/car',
                'changefreq': 'weekly',
                'priority': 0.9,
                'lastmod': datetime.now()
            },

        ]

        article_sitemap_data = article_serializers.ArticleSitemapSerializer(
            instance=article_objs, many=True, context={'route': 'article'}).data

        sitemap = sitemap + article_sitemap_data + article_sitemap_data

        return Response(sitemap)
