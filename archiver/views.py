import pdb

from django.http import HttpResponse
from django.views import View
from django.http import JsonResponse
from django.contrib.auth import authenticate


# drf imports
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from .serializers import UserSerializer
from rest_framework.permissions import IsAuthenticated

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


class Article(View):
    def get(self, request):
        return JsonResponse({"status": True})

    def post(self, request):
        return JsonResponse({"status": True})


class HealthCheck(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        return Response({"status": True})
