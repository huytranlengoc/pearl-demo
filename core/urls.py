from django.urls import path, include
from .views import RegisterApiView, LoginAPIView

urlpatterns = [
    path('register', RegisterApiView.as_view() ),
    path('login', LoginAPIView.as_view() ),

]
