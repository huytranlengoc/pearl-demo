from django.urls import path
from .views import RegisterApiView, LoginAPIView, UserAPIView, RefreshApiView, LogoutApiView, ForgetAPIView, ResetAPIView, TwoFactorAPIView

urlpatterns = [
    path('register', RegisterApiView.as_view() ),
    path('login', LoginAPIView.as_view() ),
    path('user', UserAPIView.as_view() ),
    path('refresh', RefreshApiView.as_view() ),
    path('logout', LogoutApiView.as_view() ),
    path('forgot', ForgetAPIView.as_view() ),
    path('reset', ResetAPIView.as_view() ),
    path('two-factor', TwoFactorAPIView.as_view() ),
]
