from rest_framework import exceptions
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import UserSerializer

class RegisterApiView(APIView):

    def post(self, request):
        data = request.data
        if data['password'] != data['password_confirm']:
            raise exceptions.APIException('Passwords must match')

        serializer = UserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
