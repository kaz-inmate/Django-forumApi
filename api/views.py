from rest_framework import generics, serializers, status
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import  permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from .models import *
from .serializers import *

@permission_classes((AllowAny, ))
class UserCreate(APIView):
    def post(self, request):
        serializer = UserSerializer(data = request.data)
        data = {}
        if serializer.is_valid():
            user = serializer.save()
            data['response'] ="successfully registered"
            data['email'] = user.email
            data['username'] = user.username
            token = Token.objects.get(user=user).key
            data['token'] = token
            if user:
                return Response(data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class LoginView(APIView):
#     def post(self, request):
#         username = request.data.get('username')
#         password = request.data.get('password')
#         user = authenticate(username= username, password= password)
#         if user is not None:
#             return Response({"message": "logged in successfully"},
#                             status= status.HTTP_200_OK)
#         else:
#             return Response({"error": "Wrong Credentials"}, status= status.HTTP_401_UNAUTHORIZED)


class PostView(APIView):

    permission_classes = [IsAuthenticated]

    # def perform_create(self, serializer):
    #     serializer.save(author=self.request.user)

    def get(self, request):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    
    def post(self, request, format = None):
        serializer = PostSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save(author=self.request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class PostDetail(APIView):
    
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, format=None):
        post = Post.objects.get(pk=pk)
        serializer = PostSerializer(post)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        post = Post.objects.get(pk=pk)
        user = request.user 

        if post.author != user:
            return Response({'response': "You cannot edit this post"})

        serializer = PostSerializer(post, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, pk, format=None):
        post = Post.objects.get(pk=pk)
        user = request.user 

        if post.author != user:
            return Response({'response': "You cannot delete this post"})

        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)