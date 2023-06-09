from rest_framework import exceptions
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserSerializer
from .models import User, UserToken, Reset
from .authentication import JWTAuthentication, create_access_token, create_refresh_token, decode_refresh_token
import datetime
import random, string
from django.core.mail import send_mail
import pyotp

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

        if user.tfa_secret:
            return Response({
                'id': user.id,
            })
        secret = pyotp.random_base32()
        otpauth_url = pyotp.totp.TOTP(secret).provisioning_uri(issuer_name='My App')
        return Response({
            'id': user.id,
            'secret': secret,
            'otpauth_url': otpauth_url,
        })

class TwoFactorAPIView(APIView):
    def post(self, request):
        id = request.data['id']

        user = User.objects.filter(pk=id).first()
        if not user:
            raise exceptions.AuthenticationFailed('User not found')

        secret = user.tfa_secret if user.tfa_secret else request.data['secret']
        if not pyotp.TOTP(secret).verify(request.data['code']):
            raise exceptions.AuthenticationFailed('Invalid code')

        if user.tfa_secret == '':
            user.tfa_secret = secret
            user.save()

        access_token = create_access_token(id)
        refresh_token = create_refresh_token(id)

        UserToken.objects.create(
            user_id=id,
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

class ForgetAPIView(APIView):
    def post(self, request):
        email = request.data['email']
        token = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))

        Reset.objects.create(
            email=email,
            token=token
        )

        url = 'http://localhost:8080/reset/' + token

        send_mail(
            subject='Reset your Password',
            message='Click <a href="%s">here</a> to reset your password!' % url,
            from_email='from@example.com',
            recipient_list=[email],
        )
        return Response({
            'message': 'success'
        })

class ResetAPIView(APIView):
    def post(self, request):
        data = request.data

        if data['password'] != data['password_confirm']:
            raise exceptions.APIException('Passwords must match')

        reset_password = Reset.objects.filter(token=data['token']).first()
        if not reset_password:
            raise exceptions.APIException('Invalid token')

        user = User.objects.filter(email=reset_password.email).first()
        if not user:
            raise exceptions.APIException('User not found')

        user.set_password(data['password'])
        user.save()

        return Response({
            'message': 'success'
        })
