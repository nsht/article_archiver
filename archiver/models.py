from django.db import models
from django.conf import settings

# Create your models here.


class ArticleList(models.Model):
    class Meta:
        unique_together = ("user", "article_data")

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,)
    article_data = models.ForeignKey("Article", models.SET_NULL, blank=True, null=True)
    archived = models.BooleanField(default=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # TODO: Add tag support
    def __str__(self):
        return f"User {self.user} | {self.article_data}"


class Tags(models.Model):
    class Meta:
        unique_together = ("user_article_id", "tag")

    user_article_id = models.ForeignKey(ArticleList, on_delete=models.CASCADE,)
    tag = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)


class Article(models.Model):
    # TODO: Add authors, base site, meta data
    url = models.CharField(max_length=2086)
    article_hash = models.CharField(max_length=1024)
    title = models.CharField(max_length=256, blank=True)
    byline = models.CharField(max_length=256, blank=True)
    content = models.TextField()
    textcontent = models.TextField()
    length = models.IntegerField()
    word_count = models.IntegerField(null=True)
    top_image = models.CharField(max_length=2086, null=True)
    favicon = models.CharField(max_length=2086, null=True)
    estimated_reading_time = models.IntegerField(null=True)
    excerpt = models.CharField(max_length=1024, blank=True)
    site_name = models.CharField(max_length=256, blank=True)
    publication_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Article {self.url}"

