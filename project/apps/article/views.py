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

        try:
            uid_list = article_models.CategoryGroupRank.objects.filter(slug='index').first().rank
        except Exception as e:
            uid_list = []
        all_article_list = article_models.Article.objects.exclude(uid__in=uid_list).order_by(
            'rank')[:24]
        all_article_list_data = article_serializers.ArticleSimpleSerializer(all_article_list, many=True).data

        data = {
            'trending_article_list': trending_article_list_data,
            'all_article_list': all_article_list_data
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
        sai_id = request.query_params.get('saiId', None)
        page = request.query_params.get('page', 1)
        size = request.query_params.get('size')
        return f'backend:article:search:{q}:{page}:{size}:{sai_id}'

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
            'options': ImgProxyOptions.S_COVER_IMG}).data
        if page < 2:
            sai_id = request.query_params.get('sai_id')
            style_id_info = article_models.SearchAdInfo.objects.filter(uid=sai_id).first()
            style_id_info_data = article_serializers.StyleIdSerializer(style_id_info).data

            tagList = [
                ['Donate', 'Charity', 'Non-Profit', 'Tax Deduction', 'Car Donation', 'Motorcycle', 'Boat', 'Recycle'],
                ['Blueprint', 'Design', 'Model', 'Schema', 'Prototype', 'Concept', 'Production', 'Innovation'],
                ['Car', 'Truck', 'Bike', 'Bus', 'SUV', 'Van', 'Motorcycle', 'Automobile'],
                ['Fix', 'Restore', 'Maintenance', 'Service', 'Mechanics', 'Parts', 'Replace', 'Overhaul']
            ]
            tag = [random.sample(tags, min(6, len(tags))) for tags in tagList]
            data = {
                'style_id_info': style_id_info_data,
                'tagList': tag,
                'search_article_list': search_article_list_data,
            }
        else:
            data = {'new_data_list': search_article_list_data}

        return search_articles_pg.get_paginated_response(data)



class SearchAdPageView(APIView):

    def calculate_cache_key(self, view_instance, view_method, request, args, kwargs):
        return f'backend:article:search_ad_info:{kwargs.get("uid")}:{kwargs.get("slug")}'

    @cache_response(timeout=settings.CACHE_TIME_SEARCH_AD, key_func='calculate_cache_key')
    def get(self, request, uid, slug):
        try:
            search_ad_info = article_models.SearchAdInfo.objects.get(uid=uid)
            search_article = article_models.Article.objects.get(slug=slug)
        except Exception as e:
            return APIResponse(status=drf_status.HTTP_400_BAD_REQUEST)

        search_ad_info_data = article_serializers.SearchAdInfoSerializer(search_ad_info).data
        search_article_data = article_serializers.SearchArticleSerializer(search_article).data
        data = {
            'search_ad_info': search_ad_info_data,
            'search_article': search_article_data
        }
        return APIResponse(data=data, status=drf_status.HTTP_200_OK)


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

        latest_posts_list_data = get_specify_sequence('index')[:10]

        data = {
            'category_article_list': category_article_list_data,
            'latest_posts_list': latest_posts_list_data
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
        page =5
        size = 7
        type = request.query_params.get('type', '')
        try:
            uid_list = article_models.CategoryGroupRank.objects.filter(slug=slug).first().rank
        except Exception as e:
            uid_list = []
        article_list = article_models.Article.objects.exclude(uid__in=uid_list).order_by(
            'rank')

        if type == 'category':
            article_list = article_list.filter(categories__slug=slug)
        # size = size, page = page
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
