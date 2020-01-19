import pdb

from django.http import HttpResponse
from django.views import View
from django.http import JsonResponse
from django.contrib.auth import authenticate


# drf imports
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status
from .serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated

from .utils import GetArticle

# TODO create login/user registration/logout functions http://books.agiliq.com/projects/django-api-polls-tutorial/en/latest/access-control.html
# Create your views here.
# Ref http://books.agiliq.com/projects/django-api-polls-tutorial/en/latest/access-control.html


class Index(APIView):
    def get(self, request):
        return Response({"status": True, "data": ["Home Page"]})


class UserCreate(generics.CreateAPIView):
    # Exclude from authentication
    authentication_classes = ()
    permission_classes = ()
    serializer_class = UserSerializer


class GetArticles(View):
    def get(self, request):
        return JsonResponse({"status": True, "articles": ["List of article objects"]})


class Article(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return JsonResponse({"status": True}, status=200)

    def post(self, request):
        url = request.data.get("url")
        user = request.user
        if not url:
            return Response(
                {"status": False, "error_message": "No url provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        article = GetArticle(url=url, user=user).save()
        response = {"status": True}
        if response and article:
            response.update(article)
            return Response(response)
        else:
            response["status"] = False
        return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HealthCheck(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return Response({"status": True})
