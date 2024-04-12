from django.db.models import Q, Case, When
from django_filters import rest_framework as filters

from article import models as article_models


class ArticleDataFilter(filters.FilterSet):
    uids = filters.CharFilter(method='filter_uids')
    titles = filters.CharFilter(method='filter_titles')
    descriptions = filters.CharFilter(method='filter_descriptions')
    tags = filters.CharFilter(method='filter_tags')
    categories = filters.CharFilter(method='filter_categories')

    def filter_uids(self, queryset, name, value):
        if ',' in value:
            uids = list(map(lambda x: x.strip(), value.split(',')))
            custom_order = Case(*[When(uid=uid, then=pos) for pos, uid in enumerate(uids)])
            return queryset.filter(uid__in=uids).order_by(custom_order).distinct()
        return queryset.filter(uid__icontains=value).distinct()

    def filter_titles(self, queryset, name, value):
        if ',' in value:
            titles = list(map(lambda x: x.strip(), value.split(',')))
            custom_order = Case(*[When(title=title, then=pos) for pos, title in enumerate(titles)])
            return queryset.filter(title__in=titles).order_by(custom_order).distinct()
        return queryset.filter(title__icontains=value).distinct()

    def filter_descriptions(self, queryset, name, value):
        if ',' in value:
            descriptions = list(map(lambda x: x.strip(), value.split(',')))
            custom_order = Case(
                *[When(description=description, then=pos) for pos, description in enumerate(descriptions)])
            return queryset.filter(description__in=descriptions).order_by(custom_order).distinct()
        return queryset.filter(description__icontains=value).distinct()

    def filter_tags(self, queryset, name, value):
        if ',' in value:
            tags = list(map(lambda x: x.strip(), value.split(',')))
            custom_order = Case(
                *[When(tags__name=tag, then=pos) for pos, tag in enumerate(tags)])
            return queryset.filter(tags__name__in=tags).order_by(custom_order).distinct()
        return queryset.filter(tags__name__icontains=value).distinct()

    def filter_categories(self, queryset, name, value):
        if ',' in value:
            categories = list(map(lambda x: x.strip(), value.split(',')))
            custom_order = Case(
                *[When(categories__name=category, then=pos) for pos, category in enumerate(categories)])
            return queryset.filter(categories__name__in=categories).order_by(custom_order).distinct()
        return queryset.filter(categories__name__icontains=value).distinct()

    class Meta:
        models = article_models.Article
        fields = ('uids', 'titles', 'descriptions', 'tags', 'categories')
