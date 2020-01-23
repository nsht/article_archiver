from django.contrib.auth.models import User
from .models import *
from rest_framework import serializers
from rest_framework.authtoken.models import Token


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "email", "password")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User(email=validated_data["email"], username=validated_data["username"])
        user.set_password(validated_data["password"])
        user.save()
        Token.objects.create(user=user)
        return user


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = [
            "url",
            "title",
            "byline",
            "content",
            "site_name",
            "updated_at",
            "length",
        ]


class ArticleListDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ["title", "length", "site_name"]


class ArticleListSerializer(serializers.ModelSerializer):
    article_id = ArticleListDetailSerializer()

    class Meta:
        model = ArticleList
        fields = ["created_at", "article_id"]
        depth = 1

