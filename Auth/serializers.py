from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework import generics
import django.contrib.auth.password_validation as validators
from django.core import exceptions


class CreateUserSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    class Meta:
        model = User
        fields = ('id', 'username', 'password')
        extra_kwargs = {
            'password': {'write_only': True}
        }
