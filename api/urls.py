from django.urls import path
from .views import PostView, UserCreate, PostDetail
from rest_framework.authtoken import views  #rest framework inbuilt login view

urlpatterns = [
      path('posts/', PostView.as_view(), name= 'posts-detail'),
      path('posts/<uuid:pk>', PostDetail.as_view(), name="posts-indiv"),
      path('register/', UserCreate.as_view(), name= "user_create"),
      path("login/", views.obtain_auth_token, name="get_user_auth_token"),
]