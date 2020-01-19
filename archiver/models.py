from django.db import models
from django.conf import settings

# Create your models here.


class ArticleList(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,)
    article_id = models.ForeignKey("Article", models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Article(models.Model):
    url = models.CharField(max_length=2086)
    article_hash = models.CharField(max_length=1024)
    title = models.CharField(max_length=256, blank=True)
    byline = models.CharField(max_length=256, blank=True)
    content = models.TextField()
    textcontent = models.TextField()
    lenght = models.IntegerField()
    excerpt = models.CharField(max_length=1024, blank=True)
    site_name = models.CharField(max_length=256, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

