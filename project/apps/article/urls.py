from django.urls import path

from article import views

urlpatterns = [
    path('page/index', views.IndexPageView.as_view()),
    path('page/q', views.QPageView.as_view()),
    path('data/q', views.QDataView.as_view()),
    path('page/c/<str:slug>', views.CategoryPageView.as_view()),
    path('data/c/<str:slug>', views.CategoryDataView.as_view()),
    path('page/article/<str:uid>', views.ArticlePageView.as_view()),
    path('page/Content/<str:uid>/<str:slug>', views.ContentPageView.as_view()),
    path('page/Discussion/<str:uid>/<str:slug>', views.DiscussionPageView.as_view()),

]
