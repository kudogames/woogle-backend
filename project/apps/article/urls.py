from django.urls import path

from article import views

urlpatterns = [
    path('page/index', views.IndexPageView.as_view()),
    path('page/q', views.QPageView.as_view()),
    path('page/c/<str:slug>', views.CategoryPageView.as_view()),
    path('page/article/<str:uid>', views.ArticlePageView.as_view()),
    path('page/get-data/<str:slug>', views.GetMoreDataView.as_view()),
    path('page/Content/<str:uid>/<str:slug>', views.SearchAdPageView.as_view()),

]
