from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.response import Response
from .models import MailMagazine
from Question.models import Questions


# normal serializer [similar to forms.Form]
class MailMagazineSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    order = serializers.CharField(max_length=255, required=True)
    title = serializers.CharField(max_length=255, required=True)
    content = serializers.CharField(required=True)

    # is called if we save serializer if it do not have an instance
    def create(self, validated_data):
        mailMagazine = MailMagazine.objects.create(**validated_data)
        mailMagazine.save()
        return mailMagazine

    # is called if we save serializer if it have an instance
    def update(self, instance, validated_data):
        instance.order = validated_data.get('order', instance.order)
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.save()

        return instance

    class Meta:
        model = MailMagazine
        fields = ("order", "title", "content")


# normal serializer [similar to forms.Form]
class UpdateMailMagazineSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    order = serializers.CharField(max_length=255, required=True)
    title = serializers.CharField(max_length=255, required=True)
    content = serializers.CharField(required=True)

    # is called if we save serializer if it have an instance
    def update(self, instance, validated_data):
        instance.order = validated_data.get('order', instance.order)
        instance.title = validated_data.get('title', instance.title)
        instance.content = validated_data.get('content', instance.content)
        instance.save()

        return instance

    class Meta:
        model = MailMagazine
        fields = ("order", "title", "content")
