from django.urls import path, include
from .views import RegisterApiView, LoginAPIView, UserAPIView

urlpatterns = [
    path('register', RegisterApiView.as_view() ),
    path('login', LoginAPIView.as_view() ),
    path('user', UserAPIView.as_view() ),

]
