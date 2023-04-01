from django.urls import path, include
from .views import RegisterApiView, LoginAPIView, UserAPIView, RefreshApiView, LogoutApiView

urlpatterns = [
    path('register', RegisterApiView.as_view() ),
    path('login', LoginAPIView.as_view() ),
    path('user', UserAPIView.as_view() ),
    path('refresh', RefreshApiView.as_view() ),
    path('logout', LogoutApiView.as_view() ),
]
