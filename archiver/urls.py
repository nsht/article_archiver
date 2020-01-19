from django.urls import path

from . import views

urlpatterns = [
    path("", views.Index.as_view(), name="index"),
    path("healthcheck/", views.HealthCheck.as_view(), name="healthcheck"),
    path("article/",views.Article.as_view(),name="article"),
    # user
    path("user/", views.UserCreate.as_view(), name="usercreate"),
]
