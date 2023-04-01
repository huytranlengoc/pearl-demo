from django.contrib import admin
from django.urls import path, include
from .views import RegisterApiView

urlpatterns = [
    path('register', RegisterApiView.as_view() ),
]
