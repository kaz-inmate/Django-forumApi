from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django.contrib.auth.models import User
from .models import BaseModel, Votable, Post, Comment




class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all(), message="This username is already in use.")]
    )

    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all(), message="This email is already registered.")]
    )

    password = serializers.CharField(min_length=5, write_only=True)



    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    
    def create(self, validated_data):
        user = User.objects.create_user(validated_data['username'],validated_data['email'])
        user.set_password(validated_data['password'])
        user.save()
        return user


class BaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseModel
        fields = ('created_at', 'eid',)
        abstract = True


class VoteSeriallier(BaseSerializer):
    total_count = serializers.IntegerField(source='get_score', required=False)
    class Meta:
        model = Votable
        fields =  BaseSerializer.Meta.fields + ('total_count',)
        abstract = True

class PostSerializer(VoteSeriallier):
    author = serializers.PrimaryKeyRelatedField(required=False, read_only=True)
    class Meta:
        model = Post
        fields = VoteSeriallier.Meta.fields + ('title', 'author', 'image','text','comment_count')

    def create(self, validated_data):
        post = Post.objects.create(**validated_data)
        return post

    
    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)


