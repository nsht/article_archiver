import hashlib
import json
import pdb

import requests
from .models import Article, ArticleList, Tags
from django.contrib.auth.models import User
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.core.cache import cache

from celery import shared_task
from newspaper import Article as newspaper_article

from .serializers import ArticleSerializer, ArticleListSerializer

CACHE_TTL = getattr(settings, "CACHE_TTL", DEFAULT_TIMEOUT)


class ArticleUtils:
    def __init__(self, url, user_id, tags=[]):
        self.url = url
        self.user_id = user_id
        self.user = User.objects.filter(id=user_id).first()
        self.article_hash = None
        self.tags = tags

    def save(self):
        # TODO: Move url to settings/env variables
        # TODO: Error handling
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

        if not article_id:
            return article_data

        article_list_id = ArticleList.objects.get_or_create(
            user=self.user, article_data=article_id
        )[0]
        if self.tags:
            for tag in self.tags:
                Tags.objects.get_or_create(user_article_id=article_list_id, tag=tag)

        # TODO: Add to elastic with article_list_id,user_id,datetime
        return article_data

    def get_article_id(self, article_data):
        existing_article = self.check_existing_article(article_data)
        if existing_article:
            return existing_article[0]
        # Replacing none with empty string, since CharFields were not set with null=True,
        # this was done to prevent 2 empty states in a field (null or empty string)
        article_data = {k: v if v else "" for (k, v) in article_data.items()}
        metadata = pre_process_article(self.url)
        word_count = len(article_data.get("content", "").split(" "))
        estimated_reading_time = estimate_reading_time(word_count)
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
            publication_date=metadata.get("publish_date", ""),
            top_image=metadata.get("top_image", ""),
            favicon=metadata.get("favicon"),
            word_count=word_count,
            estimated_reading_time=estimated_reading_time,
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
        user=user_id, article_data=article_id
    ).first()
    if not user_article:
        return False
    article = Article.objects.get(id=user_article.article_data_id)
    serializer = ArticleSerializer(article)
    return serializer.data


def get_article_list(user_id, serializer_context):
    articles = ArticleList.objects.filter(user=user_id)
    serializer = ArticleListSerializer(articles, many=True, context=serializer_context)
    return serializer.data


@shared_task
def save_article(url, user_id, tags):
    return ArticleUtils(url=url, user_id=user_id, tags=tags).save()


def delete_article(article_id, user_id):
    ArticleList.objects.filter(user=user_id, article_data=article_id).delete()
    return True


def pre_process_article(url):
    key = f"pre_process_article|{url}"
    data = cache.get(key)
    if not data:
        article = newspaper_article(url)
        article.download()
        article.parse()
        if article.canonical_link:
            canonical_link = article.canonical_link
        else:
            canonical_link = url
        title = article.title
        data = {}
        data["publish_date"] = article.publish_date
        data["url"] = canonical_link
        if title:
            data["title"] = title
        if article.has_top_image:
            data["top_image"] = article.top_image
        if article.meta_favicon:
            if "http" in article.meta_favicon:
                data["favicon"] = article.meta_favicon
            else:
                data["favicon"] = article.source_url + article.meta_favicon
        cache.set(key, data, timeout=CACHE_TTL)
    return data


def estimate_reading_time(total_words):
    WPM = 200
    return total_words / WPM

