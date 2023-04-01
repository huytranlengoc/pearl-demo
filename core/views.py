from rest_framework import exceptions
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserSerializer
from .models import User, UserToken
from .authentication import JWTAuthentication, create_access_token, create_refresh_token, decode_refresh_token
import datetime


class RegisterApiView(APIView):

    def post(self, request):
        data = request.data
        if data['password'] != data['password_confirm']:
            raise exceptions.APIException('Passwords must match')

        serializer = UserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

class LoginAPIView(APIView):

    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        user = User.objects.filter(email=email).first()

        if user is None:
            raise exceptions.AuthenticationFailed('User not found')

        if not user.check_password(password):
            raise exceptions.AuthenticationFailed('Incorrect password')

        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        UserToken.objects.create(
            user_id=user.id,
            refresh_token=refresh_token,
            expires_at=datetime.datetime.utcnow() + datetime.timedelta(days=7)
        )

        response = Response()
        response.set_cookie(key='refresh_token', value=refresh_token, httponly=True)
        response.data = {
            'token': access_token,
        }
        return response

class UserAPIView(APIView):
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        return Response(UserSerializer(request.user).data)

class RefreshApiView(APIView):
    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        id = decode_refresh_token(refresh_token)

        if not UserToken.objects.filter(
                user_id=id,
                refresh_token=refresh_token,
                expires_at__gt=datetime.datetime.now(tz=datetime.timezone.utc)
            ).exists():
                raise exceptions.AuthenticationFailed('unauthenticated')

        access_token = create_access_token(id)
        response = Response()
        response.data = {
            'token': access_token,
        }
        return response


class LogoutApiView(APIView):

    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token')
        UserToken.objects.filter(
            refresh_token=refresh_token,
        ).delete()

        response = Response()
        response.delete_cookie(key='refresh_token')
        response.data = {
            'message': 'success'
        }
        return response
