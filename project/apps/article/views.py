from django.db.models import Q, Case, When, IntegerField
from django.conf import settings
import random
from rest_framework import status as drf_status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_extensions.cache.decorators import cache_response

from utils.imgproxy import ImgProxyOptions
from utils.response import APIResponse
from utils.pagination import APIPageNumberPagination
from article import models as article_models
from article import serializers as article_serializers


def get_specify_sequence(uid_list_str):
    """
    首页随机文章，从15个中随机取
    """
    try:
        uid_list = article_models.CategoryGroupRank.objects.filter(slug=uid_list_str).first().rank
    except Exception as e:
        uid_list = []

    article_list = article_models.Article.objects.filter(uid__in=uid_list).order_by('?')
    article_list_data = article_serializers.ArticleSimpleSerializer(article_list, many=True).data
    return article_list_data


class IndexPageView(APIView):
    def cache_key(self, view_instance, view_method, request, args, kwargs):
        return f'backend:article:index'

    @cache_response(timeout=settings.CACHE_TIME_INDEX, key_func='cache_key')
    def get(self, request):
        trending_article_list_data = get_specify_sequence('index')[0:6]

        data = {
            'trending_article_list': trending_article_list_data,
            'all_article_list': []
        }

        return APIResponse(data=data, status=drf_status.HTTP_200_OK)


class LovePageView(APIView):
    def cache_key(self, view_instance, view_method, request, args, kwargs):
        return f'backend:article:love'

    @cache_response(timeout=settings.CACHE_TIME_LOVE, key_func='cache_key')
    def get(self, request):
        trending_article_list_data = get_specify_sequence('index')

        data = {
            'trending_article_list': trending_article_list_data,
            'all_article_list': []
        }

        return APIResponse(data=data, status=drf_status.HTTP_200_OK)


class ArticlePageView(APIView):
    def calculate_cache_key(self, view_instance, view_method, request, args, kwargs):
        return f'backend:article:{kwargs.get("uid")}'

    @cache_response(timeout=settings.CACHE_TIME_DEATAIL, key_func='calculate_cache_key')
    def get(self, request, uid):
        article_obj = article_models.Article.objects.filter(uid=uid).first()
        if not article_obj:
            return APIResponse(status=drf_status.HTTP_400_BAD_REQUEST)

        current_article_data = article_serializers.ArticleSerializer(article_obj, context={
            'options': ImgProxyOptions.L_COVER_IMG}).data

        related_article_objs = article_models.Article.objects.exclude(uid=uid).order_by('?')[:6]
        related_article_data = article_serializers.ArticleSimpleSerializer(related_article_objs, many=True, context={
            'options': ImgProxyOptions.M_COVER_IMG}).data

        data = {
            'current_article': current_article_data,
            'related_article_list': related_article_data
        }
        return APIResponse(data=data, status=drf_status.HTTP_200_OK)


class QPageView(APIView):
    def calculate_cache_key(self, view_instance, view_method, request, args, kwargs):
        q = request.query_params.get('q', None)
        page = request.query_params.get('page', 1)
        size = request.query_params.get('size')
        return f'backend:article:search:{q}:{page}:{size}'

    @cache_response(timeout=settings.CACHE_TIME_Q, key_func='calculate_cache_key')
    def get(self, request):
        page = int(request.query_params.get('page', 1))
        q = request.query_params.get('q', None)

        exact_articles = article_models.Article.objects.annotate(
            order=Case(
                When(title__icontains=q, then=0),
                When(description__icontains=q, then=1),
                default=2,
                output_field=IntegerField(),
            )
        ).order_by('order')

        search_articles_pg = APIPageNumberPagination()
        data_page = search_articles_pg.paginate_queryset(exact_articles, request)
        if data_page is None:
            return APIResponse(status=drf_status.HTTP_400_BAD_REQUEST)

        search_article_list_data = article_serializers.ArticleMiddleSerializer(data_page, many=True, context={
            'options': ImgProxyOptions.s_COVER_IMG}).data
        if page < 2:
            tagList = [
                ['Donate', 'Charity', 'Non-Profit', 'Tax Deduction', 'Car Donation', 'Motorcycle', 'Boat', 'Recycle'],
                ['Blueprint', 'Design', 'Model', 'Schema', 'Prototype', 'Concept', 'Production', 'Innovation'],
                ['Car', 'Truck', 'Bike', 'Bus', 'SUV', 'Van', 'Motorcycle', 'Automobile'],
                ['Fix', 'Restore', 'Maintenance', 'Service', 'Mechanics', 'Parts', 'Replace', 'Overhaul']
            ]
            tag = [random.sample(tags, min(6, len(tags))) for tags in tagList]
            data = {
                'tagList': tag,
                'search_article_list': search_article_list_data,
            }
        else:
            data = {'new_data_list': search_article_list_data}

        return search_articles_pg.get_paginated_response(data)


class CategoryPageView(APIView):
    def calculate_cache_key(self, view_instance, view_method, request, args, kwargs):
        return f'backend:article:category:{kwargs.get("slug")}'

    @cache_response(timeout=settings.CACHE_TIME_CATEGORY, key_func='calculate_cache_key')
    def get(self, request, slug):
        # 当前分类
        current_category = article_models.Category.objects.filter(slug=slug).first()
        if not current_category:
            return APIResponse(status=drf_status.HTTP_400_BAD_REQUEST)

        category_rank_obj = article_models.CategoryGroupRank.objects.filter(slug=slug)
        if category_rank_obj:
            uid_list = category_rank_obj.first().rank
            category_article_list = article_models.Article.objects.filter(uid__in=uid_list).order_by('rank')
        else:
            category_article_list = []
        category_article_list_data = article_serializers.ArticleMiddleSerializer(category_article_list, many=True).data

        latest_posts_list_data = get_specify_sequence('index')

        data = {
            'category_article_list': category_article_list_data,
            'latest_posts_list': latest_posts_list_data
        }

        return APIResponse(data=data, status=drf_status.HTTP_200_OK)


class AdTemplatePageView(APIView):
    def calculate_cache_key(self, view_instance, view_method, request, args, kwargs):
        page = request.query_params.get('page', 1)
        size = request.query_params.get('size')
        return f'backend:article:AdTemplate:{kwargs.get("tmpl_key_word")}:{kwargs.get("key_word")}:{page}:{size}'

    @cache_response(timeout=settings.CACHE_TIME_ADTEMPLATE, key_func='calculate_cache_key')
    def get(self, request, tmpl_key_word, key_word):
        page = int(request.query_params.get('page', 1))

        keyword_map = {
            'home': 'housing'
        }

        if tmpl_key_word not in ['offers', 'popular']:
            return APIResponse(status=drf_status.HTTP_400_BAD_REQUEST)

        keyword = keyword_map.get(key_word, key_word)

        category = article_models.Category.objects.filter(slug=keyword).first()
        # 相关文章
        related_article = category.articles.order_by(
            '?').first() if category else article_models.Article.objects.order_by('?').first()
        related_article_data = article_serializers.ArticleSimpleSerializer(related_article).data

        # 搜索文章
        search_article_list = article_models.Article.objects.annotate(
            order=Case(
                When(categories__name=keyword, then=0),
                default=1,
                output_field=IntegerField(),
            )
        ).order_by('order')

        template_articles_pg = APIPageNumberPagination()
        data_page = template_articles_pg.paginate_queryset(search_article_list, request)

        search_article_list_data = article_serializers.ArticleMiddleSerializer(data_page, many=True).data

        data = {
            'related_article': related_article_data,
            'recommend_article_list': search_article_list_data
        } if page < 2 else {'new_data_list': search_article_list_data}

        return template_articles_pg.get_paginated_response(data)


class BluePageView(APIView):
    def cache_key(self, view_instance, view_method, request, args, kwargs):
        return f'backend:article:blue'

    @cache_response(timeout=settings.CACHE_TIME_BLUE, key_func='cache_key')
    def get(self, request):
        blue_article_list = article_models.Article.objects.order_by('?')[:6]
        blue_article_data = article_serializers.ArticleSimpleSerializer(blue_article_list, many=True).data
        data = {
            'blue_article_list': blue_article_data
        }
        return APIResponse(data=data, status=drf_status.HTTP_200_OK)


class RainPageView(APIView):
    def cache_key(self, view_instance, view_method, request, args, kwargs):
        return f'backend:article:rain'

    @cache_response(timeout=settings.CACHE_TIME_RAIN, key_func='cache_key')
    def get(self, request):
        rain_uid_list = article_models.CategoryGroupRank.objects.filter(slug='rain').first().rank
        rain_article_list = article_models.Article.objects.filter(uid__in=rain_uid_list)
        rain_article_data = article_serializers.ArticleMiddleSerializer(rain_article_list, many=True, context={
            'options': ImgProxyOptions.M_COVER_IMG}).data
        data = {
            'rain_article_list': rain_article_data
        }
        return APIResponse(data=data, status=drf_status.HTTP_200_OK)


class GetMoreDataView(APIView):
    def cache_key(self, view_instance, view_method, request, args, kwargs):
        slug = kwargs.get('slug')
        page = request.query_params.get('page', 1)
        size = request.query_params.get('size')
        return f'backend:article:get_data:{slug}:{page}:{size}'

    @cache_response(timeout=settings.CACHE_TIME_GETMOREDATA, key_func='cache_key')
    def get(self, request, slug):
        type = request.query_params.get('type', '')
        try:
            uid_list = article_models.CategoryGroupRank.objects.filter(slug=slug).first().rank
        except Exception as e:
            uid_list = []
        article_list = article_models.Article.objects.exclude(uid__in=uid_list).order_by(
            'rank')

        if type == 'category':
            article_list = article_list.filter(categories__slug=slug)

        article_pg = APIPageNumberPagination()
        data_page = article_pg.paginate_queryset(article_list, request)

        if data_page is None:
            return APIResponse(status=drf_status.HTTP_400_BAD_REQUEST)
        if type == 'category':
            article_list_data = article_serializers.ArticleMiddleSerializer(data_page, many=True).data
        else:
            article_list_data = article_serializers.ArticleSimpleSerializer(data_page, many=True).data

        data = {'new_data_list': article_list_data}
        return article_pg.get_paginated_response(data)
