from django.urls import path

from . import views

urlpatterns = [
    path("", views.Index.as_view(), name="index"),
    path("healthcheck/", views.HealthCheck.as_view(), name="healthcheck"),
    path("article/", views.Article.as_view(), name="article"),
    path("article_list/", views.GetArticles.as_view(), name="article_list"),
    # user
    path("user/", views.UserCreate.as_view(), name="usercreate"),
    path("login/", views.Login.as_view(), name="login"),
    path("logout/", views.Logout.as_view(), name="logout"),
]
