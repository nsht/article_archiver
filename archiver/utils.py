import hashlib
import json
import pdb

import requests
from .models import Article, ArticleList
from django.contrib.auth.models import User
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.core.cache import cache

from celery import shared_task
from newspaper import Article as newspaper_article

from .serializers import ArticleSerializer, ArticleListSerializer

CACHE_TTL = getattr(settings, "CACHE_TTL", DEFAULT_TIMEOUT)


class ArticleUtils:
    def __init__(self, url, user_id):
        self.url = url
        self.user_id = user_id
        self.user = User.objects.filter(id=user_id).first()
        self.article_hash = None

    def save(self):
        # TODO: Move url to settings/env variables
        # TODO: Error handling
        # TODO: Caching
        # TODO: Store RAW HTML
        key = f"readability_article|{self.url}"
        article_data = cache.get(key)
        if not article_data:
            article_data = requests.get(
                "http://localhost:3000", params={"url": self.url}
            )
            if article_data.status_code != 200:
                return {}
            cache.set(key, article_data, CACHE_TTL)
        article_data = article_data.json()
        article_id = self.get_article_id(article_data)
        print(article_id)
        print(ArticleList.objects.get_or_create(user=self.user, article_id=article_id))
        return article_data

    def get_article_id(self, article_data):
        existing_article = self.check_existing_article(article_data)
        if existing_article:
            return existing_article[0]
        # Replace none with empty string, since CharFields were not set with null=True,
        # this was done to prevent 2 empty states in a field (null or empty string)
        article_data = {k: v if v else "" for (k, v) in article_data.items()}
        article = Article(
            url=self.url,
            article_hash=self.article_hash,
            title=article_data["title"],
            byline=article_data["byline"],
            content=article_data["content"],
            textcontent=article_data["textContent"],
            length=article_data["length"],
            excerpt=article_data["excerpt"],
            site_name=article_data["siteName"],
        ).save()

        return article

    def check_existing_article(self, article_data):
        self.article_hash = hashlib.sha1(
            json.dumps(article_data, sort_keys=True).encode()
        ).hexdigest()
        existing_article = Article.objects.filter(article_hash=self.article_hash)
        return existing_article


def get_article(article_id, user_id):
    user_article = ArticleList.objects.filter(
        user=user_id, article_id=article_id
    ).first()
    if not user_article:
        return False
    article = Article.objects.get(id=user_article.article_id_id)
    serializer = ArticleSerializer(article)
    return serializer.data


def get_article_list(user_id, serializer_context):
    articles = ArticleList.objects.filter(user=user_id)
    serializer = ArticleListSerializer(articles, many=True, context=serializer_context)
    return serializer.data


@shared_task
def save_article(url, user_id):
    return ArticleUtils(url=url, user_id=user_id).save()


def delete_article(article_id, user_id):
    ArticleList.objects.filter(user=user_id, article_id=article_id).delete()
    return True


def pre_process_article(url):
    key = f"pre_process_article|{url}"
    data = cache.get(key)
    if not data:
        article = newspaper_article(url)
        article.download()
        article.parse()
        title = article.title
        if title:
            data = {"title": title, "url": url}
        else:
            data = {"url": url}
        cache.set(key, data, timeout=CACHE_TTL)
    return data

