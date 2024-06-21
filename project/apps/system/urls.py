from django.urls import path
from rest_framework.routers import SimpleRouter

from system import views as system_views
from . import views

urlpatterns = [path('page/sitemap', views.SitemapPageView.as_view()),
                path('woogle-sheet-data', views.GetWoogleSheetDataView.as_view())
               ]

router = SimpleRouter(trailing_slash=False)

# 文章管理发布到站
router.register('article/article_data', system_views.ArticleDataViewSet, basename='site_data')
router.register('article/search_ad_info_data', system_views.SearchAdInfoDataViewSet, basename='site_data')
urlpatterns += router.urls
