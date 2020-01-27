import pdb

from django.http import HttpResponse
from django.views import View
from django.http import JsonResponse
from django.contrib.auth import authenticate

# drf imports
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated

from .serializers import UserSerializer
from .utils import (
    save_article,
    pre_process_article,
    get_article,
    get_article_list,
    delete_article,
)


# TODO create login/user registration/logout functions http://books.agiliq.com/projects/django-api-polls-tutorial/en/latest/access-control.html
# Create your views here.
# Ref http://books.agiliq.com/projects/django-api-polls-tutorial/en/latest/access-control.html


class Index(APIView):
    def get(self, request):
        return Response({"status": True, "data": ["Home Page"]})


class GetArticles(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user
        serializer_context = {
            "request": request,
        }
        articles = get_article_list(user.id, serializer_context=serializer_context)
        return Response({"status": True, "articles": articles})


class Article(APIView):
    permission_classes = (IsAuthenticated,)

    # TODO: error handling for logged out user
    # TODO: granular permissions ???
    def get(self, request):
        article_id = request.data.get("article_id")
        user = request.user

        article = get_article(article_id=article_id, user_id=user.id)
        if not article:
            return Response({"status": False}, status=status.HTTP_404_NOT_FOUND)
        response = {"status": True}
        response.update(article)
        return Response(response)

    def post(self, request):
        url = request.data.get("url")
        tags = request.data.get("tags")
        user = request.user
        if not url:
            return Response(
                {"status": False, "error_message": "No url provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        save_article.delay(url=url, user_id=user.id, tags=tags)
        article = pre_process_article(url=url)
        response = {"status": True}
        if response and article:
            response.update(article)
            return Response(response)
        else:
            response["status"] = False
        return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request):
        article_id = request.data.get("article_id")
        user = request.user
        if not article_id:
            return Response({"status": False})
        delete_article(article_id=article_id, user_id=user.id)
        return Response({"status": True})


class UserCreate(generics.CreateAPIView):
    # Exclude from authentication
    authentication_classes = ()
    permission_classes = ()
    serializer_class = UserSerializer


class Login(APIView):
    permission_classes = ()

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": user.auth_token.key})
        else:
            return Response(
                {"error": "Wrong Credentials"}, status=status.HTTP_400_BAD_REQUEST
            )


class Logout(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        request.user.auth_token.delete()
        return Response({"status": True}, status=status.HTTP_200_OK)


class HealthCheck(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return Response({"status": True})
