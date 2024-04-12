from django.urls import path

from article import views

urlpatterns = [
    path('page/index', views.IndexPageView.as_view()),
    path('page/love', views.LovePageView.as_view()),
    path('page/q', views.QPageView.as_view()),
    path('page/c/<str:slug>', views.CategoryPageView.as_view()),
    path('page/article/<str:uid>', views.ArticlePageView.as_view()),
    path('page/get-data/<str:slug>', views.GetMoreDataView.as_view()),
    path('page/<str:tmpl_key_word>/<str:key_word>', views.AdTemplatePageView.as_view()),
    path('page/blue', views.BluePageView.as_view()),
    path('page/rain', views.RainPageView.as_view()),

]
