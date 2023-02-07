from rest_framework import generics
from rest_framework import permissions
import json
from app.gamification.models import CustomUser
from app.gamification.serializers import UserSerializer

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


from app.gamification.models import CustomUser
from app.gamification.serializers import UserSerializer 

class Users(generics.ListCreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    def get(self, request ,*args, **kwargs):
        data = CustomUser.objects.all()

        serializer = UserSerializer(data, context={'request': request}, many=True)

        return Response(serializer.data)

class UserDetail(generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer

    def get(self, request, andrew_id, *args, **kwargs):
        try:
            data = CustomUser.objects.get(andrew_id=andrew_id)

            serializer = UserSerializer(data, context={'request': request})

            return Response(serializer.data)
        except CustomUser.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)      

class Login(generics.ListCreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer


    def post(self, request , *args, **kwargs):
        andrew_id = request.data.get('andrew_id')
        password = request.data.get('password')
        try:
            user = CustomUser.objects.get(andrew_id=andrew_id)
        except CustomUser.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if password == user.password:
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class Register(generics.ListCreateAPIView):
    def post(self, request, *args, **kwargs):

        
        andrew_id = request.data.get('andrew_id')
        password = request.data.get('password')

        try:
            user = CustomUser.objects.get(andrew_id=andrew_id)
        except CustomUser.DoesNotExist:
            user = CustomUser.objects.create(andrew_id=andrew_id)
            user.set_password(password)
            user.save()
            return Response(status=status.HTTP_200_OK)

        return Response(status=status.HTTP_400_BAD_REQUEST)


