"""
项目主路由

eg:
    /api/v1/game/page/index
    /api/v1/game/page/detail
    /api/v1/game/page/play
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django 后台
    path('kukudoadmin/', admin.site.urls),
    # 管理 API
    path('api/v1/system/', include('system.urls')),
    # API
    path('api/v1/article/', include('article.urls')),
]
